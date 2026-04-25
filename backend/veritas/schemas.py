from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class InputKind(str, Enum):
    TEXT = "text"
    URL = "url"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class Verdict(str, Enum):
    TRUE = "TRUE"
    MOSTLY_TRUE = "MOSTLY_TRUE"
    MIXED = "MIXED"
    MISLEADING = "MISLEADING"
    FALSE = "FALSE"
    UNVERIFIABLE = "UNVERIFIABLE"
    SATIRE = "SATIRE"


class Stance(str, Enum):
    SUPPORTS = "supports"
    REFUTES = "refutes"
    CONTEXT = "context"


class Source(BaseModel):
    id: int
    url: str
    title: str | None = None
    publisher: str | None = None
    domain: str | None = None
    credibility: float = Field(0.5, ge=0.0, le=1.0)
    bias: str = "unknown"  # left | center-left | center | center-right | right | unknown
    kind: str = "news"      # news | blog | social | fact_check | official | scientific | satire
    date: datetime | None = None


class Evidence(BaseModel):
    source_id: int
    quote: str
    stance: Stance = Stance.CONTEXT
    agent: str = "web_research"


class Claim(BaseModel):
    text: str
    who: str | None = None
    what: str | None = None
    when: str | None = None
    where: str | None = None


class ClaimPacket(BaseModel):
    raw_input: str
    kind: InputKind
    normalized_text: str = ""
    url: str | None = None
    fetched_title: str | None = None
    fetched_publisher: str | None = None


class RubricBreakdown(BaseModel):
    source_credibility: float
    source_diversity: float
    evidence_strength: float
    fact_checker_consensus: float
    media_authenticity: float
    temporal_integrity: float
    original_source_traceability: float


class CheckResult(BaseModel):
    trace_id: str
    verdict: Verdict
    legitimacy_score: int  # 0-100
    confidence: float
    tl_dr: str
    claims: list[Claim]
    sources: list[Source]
    evidence: list[Evidence]
    rubric: RubricBreakdown
    red_flags: list[str] = []
    why_might_i_be_wrong: str = ""
    critic_notes: str = ""
    generated_at: datetime
    extras: dict[str, Any] = {}


class CheckRequest(BaseModel):
    input: str
