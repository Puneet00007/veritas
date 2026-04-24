"""Supervisor that runs sub-agents in parallel and aggregates results.

Kept as a plain asyncio orchestrator for now (no LangGraph dep) so the
MVP has zero external runtime prerequisites. Swapping in LangGraph later
is a localized change.
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from .agents import claim_extractor, critic, fact_check_registry, reddit, synthesizer, web_research
from .agents.source_credibility import build_source
from .credibility_data import SATIRE
from .intake import build_packet
from .llm import LLM
from .schemas import CheckResult, ClaimPacket, Evidence, Source, Stance
from .scoring import compute_rubric, confidence_from_signals, pick_verdict, weighted_score


def _trace_id(raw: str) -> str:
    return hashlib.sha1(f"{raw}{time.time_ns()}".encode()).hexdigest()[:12]


def _score_stance_from_snippet(snippet: str, claim_text: str) -> Stance:
    """Very lightweight stance classifier.

    In production this is an LLM call per (snippet, claim) pair, re-ranked
    by cross-encoder. For the MVP we use cheap lexical heuristics so the
    pipeline is fully functional even without an LLM key.
    """
    s = snippet.lower()
    negatives = (
        "false",
        "debunked",
        "misleading",
        "no evidence",
        "not true",
        "incorrect",
        "hoax",
        "fake",
        "disputed",
        "myth",
    )
    positives = (
        "confirmed",
        "verified",
        "accurate",
        "true",
        "corroborated",
        "consistent with",
    )
    if any(n in s for n in negatives):
        return Stance.REFUTES
    if any(p in s for p in positives):
        return Stance.SUPPORTS
    return Stance.CONTEXT


class Orchestrator:
    def __init__(self) -> None:
        self.llm = LLM()

    async def run(self, raw_input: str) -> CheckResult:
        events: list[tuple[str, dict]] = []
        async for _ in self.run_stream(raw_input, _sink=events):
            pass
        # last "result" event holds the final CheckResult dict
        for name, payload in reversed(events):
            if name == "result":
                return CheckResult(**payload)
        raise RuntimeError("no result produced")

    async def run_stream(
        self,
        raw_input: str,
        *,
        _sink: list | None = None,
    ) -> AsyncIterator[tuple[str, dict]]:
        trace_id = _trace_id(raw_input)

        def emit(name: str, payload: dict) -> tuple[str, dict]:
            ev = (name, {"trace_id": trace_id, **payload})
            if _sink is not None:
                _sink.append(ev)
            return ev

        yield emit("start", {"message": "Normalizing input"})
        packet: ClaimPacket = await build_packet(raw_input)
        yield emit(
            "intake",
            {
                "kind": packet.kind.value,
                "url": packet.url,
                "title": packet.fetched_title,
                "publisher": packet.fetched_publisher,
            },
        )

        # Satire short-circuit on URL input.
        satire_flag = bool(
            packet.fetched_publisher and packet.fetched_publisher.lower().removeprefix("www.") in SATIRE
        )
        if satire_flag:
            yield emit("satire_detected", {"domain": packet.fetched_publisher})

        yield emit("claim_extraction", {"message": "Extracting atomic claims"})
        claims = await claim_extractor.extract_claims(packet, self.llm)
        yield emit("claims", {"claims": [c.model_dump() for c in claims]})

        yield emit("fanout", {"agents": ["web_research", "fact_check_registry", "reddit"]})
        web_task = asyncio.create_task(web_research.research(claims))
        fc_task = asyncio.create_task(fact_check_registry.lookup(claims))
        reddit_task = asyncio.create_task(reddit.signal(claims))

        web_hits, fc_hits, reddit_hits = await asyncio.gather(web_task, fc_task, reddit_task)
        yield emit(
            "agent_results",
            {
                "web_hits": len(web_hits),
                "fact_check_hits": len(fc_hits),
                "reddit_hits": len(reddit_hits),
            },
        )

        # Build Source registry (deduped by URL).
        sources: list[Source] = []
        url_to_id: dict[str, int] = {}

        def add_source(url: str, title: str | None, publisher: str | None = None) -> int:
            if not url:
                return -1
            if url in url_to_id:
                return url_to_id[url]
            sid = len(sources) + 1
            sources.append(build_source(sid, url, title, publisher))
            url_to_id[url] = sid
            return sid

        if packet.url:
            add_source(packet.url, packet.fetched_title, packet.fetched_publisher)

        evidence: list[Evidence] = []

        for h in web_hits:
            sid = add_source(h.get("url", ""), h.get("title"))
            if sid < 0:
                continue
            snippet = (h.get("snippet") or "").strip()
            if not snippet:
                continue
            claim_text = claims[h["claim_id"]].text if h.get("claim_id", 0) < len(claims) else ""
            evidence.append(
                Evidence(
                    source_id=sid,
                    quote=snippet[:400],
                    stance=_score_stance_from_snippet(snippet, claim_text),
                    agent="web_research",
                )
            )

        for h in fc_hits:
            sid = add_source(h.get("url", ""), h.get("title"), h.get("publisher_site") or h.get("publisher"))
            if sid < 0:
                continue
            rating = h.get("rating_normalized", "UNKNOWN")
            stance = Stance.CONTEXT
            if rating in {"FALSE", "MISLEADING"}:
                stance = Stance.REFUTES
            elif rating in {"TRUE", "MOSTLY_TRUE"}:
                stance = Stance.SUPPORTS
            evidence.append(
                Evidence(
                    source_id=sid,
                    quote=f'{h.get("publisher", "Fact checker")} rated: "{h.get("rating", "unknown")}"',
                    stance=stance,
                    agent="fact_check_registry",
                )
            )

        for h in reddit_hits[:6]:
            sid = add_source(h.get("url", ""), h.get("title"), "reddit.com")
            if sid < 0:
                continue
            text = f'r/{h.get("subreddit","")}: "{h.get("title","")}" ({h.get("score",0)} upvotes, {h.get("num_comments",0)} comments)'
            evidence.append(
                Evidence(
                    source_id=sid,
                    quote=text,
                    stance=_score_stance_from_snippet(h.get("title", ""), ""),
                    agent="reddit",
                )
            )

        rubric = compute_rubric(sources, evidence, fc_hits)
        score = weighted_score(rubric)
        verdict, base_conf = pick_verdict(score, fc_hits, evidence, sources, satire_flag)
        confidence = round((base_conf + confidence_from_signals(sources, evidence)) / 2, 2)

        yield emit(
            "draft_verdict",
            {"verdict": verdict.value, "score": score, "confidence": confidence},
        )

        # Critic pass (may veto once; re-run isn't implemented in MVP but we
        # expose the critic's notes to the user so they see the self-review).
        critic_data = await critic.review(self.llm, verdict, sources, evidence)
        yield emit("critic", critic_data)

        syn = await synthesizer.synthesize(self.llm, claims, sources, evidence, verdict, score)
        yield emit("synthesizer", {"tl_dr": syn["tl_dr"]})

        result = CheckResult(
            trace_id=trace_id,
            verdict=verdict,
            legitimacy_score=score,
            confidence=confidence,
            tl_dr=syn["tl_dr"],
            claims=claims,
            sources=sources,
            evidence=evidence,
            rubric=rubric,
            red_flags=syn["red_flags"],
            why_might_i_be_wrong=syn["why_might_i_be_wrong"],
            critic_notes=critic_data.get("notes", ""),
            generated_at=datetime.now(timezone.utc),
            extras={
                "input_kind": packet.kind.value,
                "input_url": packet.url,
                "llm_mock": self.llm.is_mock,
            },
        )
        yield emit("result", result.model_dump(mode="json"))
