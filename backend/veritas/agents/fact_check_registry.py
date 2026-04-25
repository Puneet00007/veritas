from __future__ import annotations

import asyncio
from typing import Any

import httpx

from ..config import settings
from ..schemas import Claim

GOOGLE_API = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


async def _google_search(query: str) -> list[dict[str, Any]]:
    if not settings.google_fact_check_api_key:
        return []
    params = {
        "query": query,
        "languageCode": "en",
        "pageSize": 8,
        "key": settings.google_fact_check_api_key,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(GOOGLE_API, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return []

    out: list[dict[str, Any]] = []
    for c in data.get("claims", []) or []:
        for review in c.get("claimReview", []) or []:
            rating = (review.get("textualRating") or "").strip()
            out.append(
                {
                    "claim_text": c.get("text", ""),
                    "rating": rating,
                    "rating_normalized": _normalize_rating(rating),
                    "url": review.get("url", ""),
                    "title": review.get("title", ""),
                    "publisher": (review.get("publisher") or {}).get("name", ""),
                    "publisher_site": (review.get("publisher") or {}).get("site", ""),
                    "date": review.get("reviewDate", ""),
                }
            )
    return out


def _normalize_rating(text: str) -> str:
    """Map free-form fact-checker ratings to our verdict buckets."""
    t = text.lower()
    if not t:
        return "UNKNOWN"
    if any(k in t for k in ("true", "correct", "accurate", "verdadero")):
        if any(k in t for k in ("mostly", "partially", "half")):
            return "MOSTLY_TRUE"
        return "TRUE"
    if any(k in t for k in ("false", "pants on fire", "incorrect", "falso", "bogus", "fake")):
        return "FALSE"
    if any(k in t for k in ("misleading", "missing context", "out of context", "distorted")):
        return "MISLEADING"
    if any(k in t for k in ("unproven", "unverified", "disputed", "no evidence")):
        return "UNVERIFIABLE"
    if "satire" in t:
        return "SATIRE"
    if any(k in t for k in ("mixed", "half")):
        return "MIXED"
    return "UNKNOWN"


async def lookup(claims: list[Claim]) -> list[dict[str, Any]]:
    async def one(idx: int, claim: Claim) -> list[dict[str, Any]]:
        hits = await _google_search(claim.text)
        for h in hits:
            h["claim_id"] = idx
        return hits

    batches = await asyncio.gather(*[one(i, c) for i, c in enumerate(claims)])
    flat: list[dict[str, Any]] = []
    for b in batches:
        flat.extend(b)
    return flat
