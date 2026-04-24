from __future__ import annotations

from ..credibility_data import score_for_domain
from ..intake import parse_domain
from ..schemas import Source


def build_source(sid: int, url: str, title: str | None, publisher: str | None = None) -> Source:
    domain = parse_domain(url) or (publisher or "")
    cred, bias, kind = score_for_domain(domain) if domain else (0.5, "unknown", "news")
    return Source(
        id=sid,
        url=url,
        title=title,
        publisher=publisher or domain or None,
        domain=domain or None,
        credibility=cred,
        bias=bias,
        kind=kind,
    )
