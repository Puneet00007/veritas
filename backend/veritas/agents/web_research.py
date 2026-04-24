from __future__ import annotations

import asyncio
from typing import Any

import httpx

from ..config import settings
from ..schemas import Claim


async def _tavily_search(query: str, max_results: int = 6) -> list[dict[str, Any]]:
    if not settings.tavily_api_key:
        return []
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "search_depth": "advanced",
        "include_answer": False,
        "max_results": max_results,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
        except Exception:
            return []
    out: list[dict[str, Any]] = []
    for item in data.get("results", []):
        out.append(
            {
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "score": item.get("score", 0.5),
            }
        )
    return out


async def _duckduckgo_search(query: str, max_results: int = 6) -> list[dict[str, Any]]:
    """Lightweight fallback using DuckDuckGo's HTML endpoint.

    This is best-effort; for production prefer Tavily/Brave/Exa.
    """
    url = "https://duckduckgo.com/html/"
    headers = {"User-Agent": "Mozilla/5.0 VeritasBot/0.1"}
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            r = await client.get(url, params={"q": query}, headers=headers)
            r.raise_for_status()
            html = r.text
    except Exception:
        return []

    import re

    results: list[dict[str, Any]] = []
    for m in re.finditer(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
        r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
        html,
        flags=re.S,
    ):
        link, title, snippet = m.groups()
        results.append(
            {
                "url": _strip_ddg(link),
                "title": _strip_tags(title),
                "snippet": _strip_tags(snippet),
                "score": 0.5,
            }
        )
        if len(results) >= max_results:
            break
    return results


def _strip_tags(s: str) -> str:
    import re

    return re.sub(r"<[^>]+>", "", s).strip()


def _strip_ddg(u: str) -> str:
    from urllib.parse import parse_qs, urlparse

    try:
        parsed = urlparse(u)
        if parsed.path == "/l/":
            q = parse_qs(parsed.query)
            if "uddg" in q:
                from urllib.parse import unquote

                return unquote(q["uddg"][0])
    except Exception:
        pass
    return u


async def research(claims: list[Claim], per_claim: int = 4) -> list[dict[str, Any]]:
    """For each claim, run one search and return flattened hits with claim_id attached."""

    async def one(idx: int, claim: Claim) -> list[dict[str, Any]]:
        q = claim.text
        hits = await _tavily_search(q, max_results=per_claim)
        if not hits:
            hits = await _duckduckgo_search(q, max_results=per_claim)
        for h in hits:
            h["claim_id"] = idx
        return hits

    batches = await asyncio.gather(*[one(i, c) for i, c in enumerate(claims)])
    flat: list[dict[str, Any]] = []
    for b in batches:
        flat.extend(b)
    return flat
