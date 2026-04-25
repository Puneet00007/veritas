from __future__ import annotations

import json

from ..llm import LLM
from ..schemas import Evidence, Source, Verdict

CRITIC_SYSTEM = (
    "You are the CRITIC / RED-TEAM agent. Your job is to look for weaknesses in a draft verdict. "
    "Given the verdict, sources, and evidence, ask 'what would it take for this to be wrong?'. "
    "If a plausible counter-argument is NOT addressed, set needs_another_round=true. "
    "Return JSON: {\"needs_another_round\": bool, \"issues\": [str, ...], \"notes\": str}."
)


async def review(
    llm: LLM,
    verdict: Verdict,
    sources: list[Source],
    evidence: list[Evidence],
) -> dict:
    ctx = {
        "draft_verdict": verdict.value,
        "source_count": len(sources),
        "distinct_domains": len({s.domain for s in sources if s.domain}),
        "has_fact_checker": any(s.kind == "fact_check" for s in sources),
        "supports": sum(1 for e in evidence if e.stance.value == "supports"),
        "refutes": sum(1 for e in evidence if e.stance.value == "refutes"),
    }
    data = await llm.json(CRITIC_SYSTEM, json.dumps(ctx, ensure_ascii=False), temperature=0.3)
    return {
        "needs_another_round": bool(data.get("needs_another_round", False)),
        "issues": data.get("issues") or [],
        "notes": data.get("notes") or "",
    }
