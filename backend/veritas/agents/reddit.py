"""Reddit signal agent.

Strategy (since the official Reddit API is heavily restricted in 2026):
1. Use the public `.json` endpoint with a rotating UA.
2. Weight results from high-signal subs: r/IsItBullshit, r/OutOfTheLoop,
   r/AskHistorians, r/NoStupidQuestions, r/SkepticQuestions, r/AskScience.
"""

from __future__ import annotations

import asyncio
import html
from typing import Any

import httpx

from ..schemas import Claim

HIGH_SIGNAL_SUBS = {
    "IsItBullshit": 1.0,
    "AskHistorians": 0.95,
    "AskScience": 0.90,
    "AskSocialScience": 0.85,
    "OutOfTheLoop": 0.80,
    "SkepticQuestions": 0.85,
    "science": 0.75,
    "news": 0.60,
    "worldnews": 0.55,
    "conspiracy": 0.15,
}

HEADERS = {"User-Agent": "veritas/0.1 (fact-checking bot)"}


async def _search(query: str, limit: int = 8) -> list[dict[str, Any]]:
    url = "https://www.reddit.com/search.json"
    params = {
        "q": query,
        "sort": "relevance",
        "t": "year",
        "limit": limit,
        "raw_json": 1,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return []

    out: list[dict[str, Any]] = []
    for child in (data.get("data") or {}).get("children", []) or []:
        d = child.get("data", {})
        sub = d.get("subreddit", "")
        weight = HIGH_SIGNAL_SUBS.get(sub, 0.35)
        out.append(
            {
                "title": html.unescape(d.get("title", "")),
                "subreddit": sub,
                "url": "https://www.reddit.com" + d.get("permalink", ""),
                "score": d.get("score", 0),
                "num_comments": d.get("num_comments", 0),
                "selftext": (d.get("selftext") or "")[:400],
                "signal_weight": weight,
            }
        )
    return out


async def signal(claims: list[Claim], per_claim: int = 5) -> list[dict[str, Any]]:
    async def one(idx: int, claim: Claim) -> list[dict[str, Any]]:
        hits = await _search(claim.text, limit=per_claim)
        for h in hits:
            h["claim_id"] = idx
        return hits

    batches = await asyncio.gather(*[one(i, c) for i, c in enumerate(claims)])
    flat: list[dict[str, Any]] = []
    for b in batches:
        flat.extend(b)
    flat.sort(key=lambda x: x["signal_weight"] * (1 + 0.01 * x.get("score", 0)), reverse=True)
    return flat[:20]
