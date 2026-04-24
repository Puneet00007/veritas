from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx
import tldextract

from .schemas import ClaimPacket, InputKind

URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)


def detect_kind(raw: str) -> tuple[InputKind, str | None]:
    raw = raw.strip()
    m = URL_RE.search(raw)
    if m:
        return InputKind.URL, m.group(0).rstrip(").,")
    return InputKind.TEXT, None


def canonical_domain(url: str) -> str:
    ext = tldextract.extract(url)
    return ".".join(p for p in [ext.domain, ext.suffix] if p)


async def fetch_url(url: str, timeout: float = 15.0) -> tuple[str, str | None, str | None]:
    """Fetch a URL and extract the main textual content.

    Returns (text, title, publisher_domain).
    """
    from trafilatura import extract as trafi_extract
    from trafilatura import extract_metadata

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0 Safari/537.36 VeritasBot/0.1"
        ),
        "Accept": "text/html,application/xhtml+xml",
    }
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        try:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            html = r.text
        except Exception:
            return "", None, canonical_domain(url)

    text = trafi_extract(html, include_comments=False, include_tables=False) or ""
    title: str | None = None
    try:
        md = extract_metadata(html)
        if md:
            title = md.title
    except Exception:
        pass

    return text.strip(), title, canonical_domain(url)


async def build_packet(raw_input: str) -> ClaimPacket:
    kind, url = detect_kind(raw_input)
    if kind == InputKind.URL and url:
        text, title, publisher = await fetch_url(url)
        normalized = text if text else raw_input
        return ClaimPacket(
            raw_input=raw_input,
            kind=kind,
            normalized_text=normalized[:8000],
            url=url,
            fetched_title=title,
            fetched_publisher=publisher,
        )
    return ClaimPacket(
        raw_input=raw_input,
        kind=InputKind.TEXT,
        normalized_text=raw_input.strip()[:8000],
    )


def parse_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.removeprefix("www.")
    except Exception:
        return ""
