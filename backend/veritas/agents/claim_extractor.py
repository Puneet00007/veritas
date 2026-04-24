from __future__ import annotations

from ..llm import LLM
from ..schemas import Claim, ClaimPacket

CLAIM_SYSTEM = (
    "You are a fact-checking assistant. Extract the ATOMIC, CHECKABLE claims from the input. "
    "Skip opinions, jokes, rhetorical questions, tautologies, and pure value judgments. "
    "For each claim, fill who/what/when/where when obvious. "
    "Return JSON: {\"claims\": [{\"text\": str, \"who\": str|null, \"what\": str|null, "
    "\"when\": str|null, \"where\": str|null}, ...]}"
)


async def extract_claims(packet: ClaimPacket, llm: LLM, max_claims: int = 5) -> list[Claim]:
    user = packet.normalized_text or packet.raw_input
    if packet.fetched_title:
        user = f"Headline: {packet.fetched_title}\n\nContent:\n{user}"
    data = await llm.json(CLAIM_SYSTEM, user)
    raw = data.get("claims") or []
    claims: list[Claim] = []
    for c in raw[:max_claims]:
        if isinstance(c, dict) and c.get("text"):
            claims.append(Claim(**{k: c.get(k) for k in ("text", "who", "what", "when", "where")}))
        elif isinstance(c, str):
            claims.append(Claim(text=c))
    if not claims:
        claims.append(Claim(text=(packet.normalized_text or packet.raw_input)[:300]))
    return claims
