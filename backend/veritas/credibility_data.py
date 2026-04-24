"""Seed domain credibility + bias map.

This is a *small*, opinionated starter set. Full production would ingest
MBFC / Ad Fontes / NewsGuard data nightly. Scores are 0-1 where
1 = tier-1 wire/reference, 0 = known-misinformation domain.
"""

from __future__ import annotations

# Tier-1: wire services, reference works, top-of-class science publishers.
TIER_1 = {
    "reuters.com": 0.95,
    "apnews.com": 0.95,
    "bbc.com": 0.90,
    "bbc.co.uk": 0.90,
    "npr.org": 0.88,
    "pbs.org": 0.88,
    "economist.com": 0.88,
    "ft.com": 0.88,
    "wsj.com": 0.86,
    "nytimes.com": 0.85,
    "washingtonpost.com": 0.84,
    "nature.com": 0.95,
    "science.org": 0.95,
    "who.int": 0.92,
    "cdc.gov": 0.92,
    "nih.gov": 0.92,
    "un.org": 0.90,
    "wikipedia.org": 0.80,
    "wikidata.org": 0.85,
    "arxiv.org": 0.80,
    "pubmed.ncbi.nlm.nih.gov": 0.93,
}

# Fact-checkers (IFCN signatories and well-known verifiers).
FACT_CHECKERS = {
    "snopes.com": 0.90,
    "politifact.com": 0.88,
    "factcheck.org": 0.90,
    "apnews.com/hub/ap-fact-check": 0.92,
    "reuters.com/fact-check": 0.92,
    "fullfact.org": 0.90,
    "factcheck.afp.com": 0.88,
    "boomlive.in": 0.86,
    "altnews.in": 0.86,
    "factly.in": 0.85,
    "chequeado.com": 0.86,
    "maldita.es": 0.86,
    "correctiv.org": 0.86,
    "africacheck.org": 0.86,
    "pesacheck.org": 0.83,
    "dubawa.org": 0.83,
    "rappler.com": 0.82,
}

# Mainstream but opinionated / clearly partisan outlets.
TIER_2 = {
    "theguardian.com": 0.80,
    "bloomberg.com": 0.82,
    "cnbc.com": 0.78,
    "cnn.com": 0.72,
    "foxnews.com": 0.60,
    "msnbc.com": 0.65,
    "politico.com": 0.78,
    "theatlantic.com": 0.76,
    "forbes.com": 0.65,
    "time.com": 0.78,
    "newsweek.com": 0.65,
    "huffpost.com": 0.60,
    "breitbart.com": 0.35,
    "dailymail.co.uk": 0.40,
    "thesun.co.uk": 0.35,
    "nypost.com": 0.50,
}

# Satire — we treat these specially (claim satire detected → verdict = SATIRE).
SATIRE = {
    "theonion.com",
    "babylonbee.com",
    "clickhole.com",
    "thebeaverton.com",
    "thehardtimes.net",
    "reductress.com",
    "newsthump.com",
    "thepoke.co.uk",
}

# Known misinformation amplifiers (Iffy.news-style starter list).
LOW_CREDIBILITY = {
    "infowars.com": 0.05,
    "naturalnews.com": 0.05,
    "beforeitsnews.com": 0.05,
    "worldtruth.tv": 0.05,
    "yournewswire.com": 0.05,
    "thegatewaypundit.com": 0.15,
    "zerohedge.com": 0.25,
    "rt.com": 0.25,
    "sputniknews.com": 0.20,
    "presstv.ir": 0.20,
}


BIAS_MAP = {
    "foxnews.com": "right",
    "breitbart.com": "right",
    "thegatewaypundit.com": "right",
    "dailymail.co.uk": "right",
    "nypost.com": "right",
    "wsj.com": "center-right",
    "economist.com": "center-right",
    "bbc.com": "center",
    "reuters.com": "center",
    "apnews.com": "center",
    "npr.org": "center-left",
    "theatlantic.com": "center-left",
    "nytimes.com": "center-left",
    "washingtonpost.com": "center-left",
    "theguardian.com": "center-left",
    "msnbc.com": "left",
    "huffpost.com": "left",
    "cnn.com": "center-left",
}

KIND_MAP: dict[str, str] = {d: "fact_check" for d in FACT_CHECKERS}
KIND_MAP.update({d: "satire" for d in SATIRE})
for d in ("who.int", "cdc.gov", "nih.gov", "un.org"):
    KIND_MAP[d] = "official"
for d in ("nature.com", "science.org", "arxiv.org", "pubmed.ncbi.nlm.nih.gov"):
    KIND_MAP[d] = "scientific"

ALL_SCORES: dict[str, float] = {}
for table in (TIER_1, FACT_CHECKERS, TIER_2, LOW_CREDIBILITY):
    ALL_SCORES.update(table)


def score_for_domain(domain: str) -> tuple[float, str, str]:
    """Return (credibility, bias, kind) for a domain, with sensible defaults."""
    d = domain.lower().removeprefix("www.")
    if d in SATIRE:
        return 0.10, "unknown", "satire"
    if d in ALL_SCORES:
        return ALL_SCORES[d], BIAS_MAP.get(d, "unknown"), KIND_MAP.get(d, "news")
    # Fallback heuristic: gov/edu → moderate trust; social → low; unknown → 0.5
    if d.endswith(".gov") or d.endswith(".gov.uk"):
        return 0.85, "unknown", "official"
    if d.endswith(".edu") or d.endswith(".ac.uk"):
        return 0.80, "unknown", "scientific"
    if d in {"x.com", "twitter.com", "reddit.com", "facebook.com", "tiktok.com", "instagram.com"}:
        return 0.35, "unknown", "social"
    return 0.50, "unknown", "news"
