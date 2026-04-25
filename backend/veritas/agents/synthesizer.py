from __future__ import annotations

import json

from ..llm import LLM
from ..schemas import Claim, Evidence, Source, Verdict

SYN_SYSTEM = (
    "You are the SYNTHESIZER agent of a fact-checking system. "
    "Given the extracted claims, retrieved sources, and stance-tagged evidence, "
    "write a concise, neutral TL;DR (2-4 sentences) explaining the verdict. "
    "Then write a short 'why_might_i_be_wrong' paragraph (2-3 sentences) "
    "that candidly surfaces the strongest counter-argument or uncertainty. "
    "Return JSON: {\"tl_dr\": str, \"why_might_i_be_wrong\": str, \"red_flags\": [str, ...]}"
)


async def synthesize(
    llm: LLM,
    claims: list[Claim],
    sources: list[Source],
    evidence: list[Evidence],
    verdict: Verdict,
    score: int,
) -> dict:
    ctx = {
        "verdict": verdict.value,
        "legitimacy_score": score,
        "claims": [c.model_dump() for c in claims],
        "sources": [
            {
                "id": s.id,
                "url": s.url,
                "publisher": s.publisher,
                "credibility": s.credibility,
                "kind": s.kind,
                "bias": s.bias,
            }
            for s in sources[:12]
        ],
        "evidence": [e.model_dump() for e in evidence[:20]],
    }
    data = await llm.json(SYN_SYSTEM, json.dumps(ctx, ensure_ascii=False), temperature=0.2)
    return {
        "tl_dr": data.get("tl_dr") or _fallback_tldr(verdict, sources),
        "why_might_i_be_wrong": data.get("why_might_i_be_wrong") or _fallback_why_wrong(verdict),
        "red_flags": data.get("red_flags") or _auto_red_flags(sources, evidence),
    }


def _fallback_tldr(verdict: Verdict, sources: list[Source]) -> str:
    return (
        f"Based on {len(sources)} retrieved sources, the current verdict is {verdict.value}. "
        f"See the evidence list and rubric breakdown for the drivers."
    )


def _fallback_why_wrong(verdict: Verdict) -> str:
    if verdict in (Verdict.TRUE, Verdict.MOSTLY_TRUE):
        return (
            "The verdict could be wrong if the top-ranked sources are all citing a single "
            "unverified primary source, or if a credible refutation was published after retrieval."
        )
    if verdict in (Verdict.FALSE, Verdict.MISLEADING):
        return (
            "The verdict could be wrong if the cited refutations rely on outdated information, "
            "or if a narrow literal interpretation is being mistaken for the claim's substance."
        )
    return "With this much uncertainty, additional primary-source evidence could flip the call."


def _auto_red_flags(sources: list[Source], evidence: list[Evidence]) -> list[str]:
    flags: list[str] = []
    if not sources:
        flags.append("no_retrieved_sources")
    low_cred = [s for s in sources if s.credibility < 0.4]
    if low_cred and len(low_cred) >= len(sources) / 2:
        flags.append("majority_low_credibility_sources")
    kinds = {s.kind for s in sources}
    if "fact_check" not in kinds:
        flags.append("no_dedicated_fact_checker_match")
    return flags
