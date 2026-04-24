"""Transparent legitimacy score rubric (0-100).

Weights:
  source_credibility              25
  source_diversity                10
  evidence_strength               25
  fact_checker_consensus          15
  media_authenticity              10   (neutral=100 when no media in MVP)
  temporal_integrity               5   (neutral=100 in MVP)
  original_source_traceability    10

Confidence is derived separately from evidence volume and stance agreement.
"""

from __future__ import annotations

from collections import Counter

from .schemas import Evidence, RubricBreakdown, Source, Stance, Verdict

WEIGHTS = {
    "source_credibility": 25,
    "source_diversity": 10,
    "evidence_strength": 25,
    "fact_checker_consensus": 15,
    "media_authenticity": 10,
    "temporal_integrity": 5,
    "original_source_traceability": 10,
}


def score_source_credibility(sources: list[Source]) -> float:
    if not sources:
        return 0.0
    top = sorted(sources, key=lambda s: s.credibility, reverse=True)[:5]
    return sum(s.credibility for s in top) / len(top) * 100.0


def score_source_diversity(sources: list[Source]) -> float:
    if not sources:
        return 0.0
    distinct_domains = {s.domain for s in sources if s.domain}
    return min(100.0, len(distinct_domains) * 20.0)


def score_evidence_strength(evidence: list[Evidence], sources: list[Source]) -> float:
    if not evidence:
        return 0.0
    by_id = {s.id: s for s in sources}
    support = 0.0
    refute = 0.0
    for e in evidence:
        s = by_id.get(e.source_id)
        w = s.credibility if s else 0.5
        if e.stance == Stance.SUPPORTS:
            support += w
        elif e.stance == Stance.REFUTES:
            refute += w
    total = support + refute
    if total == 0:
        return 40.0  # neutral-ish
    # A clear majority on one side boosts score.
    dominance = max(support, refute) / total
    return min(100.0, 40.0 + dominance * 60.0)


def score_fact_checker_consensus(fact_check_hits: list[dict]) -> float:
    if not fact_check_hits:
        return 50.0
    normalized = [h.get("rating_normalized", "UNKNOWN") for h in fact_check_hits]
    counter = Counter(normalized)
    majority, count = counter.most_common(1)[0]
    ratio = count / sum(counter.values())
    if majority == "UNKNOWN":
        return 50.0
    return min(100.0, 50.0 + ratio * 50.0)


def score_original_source_traceability(sources: list[Source]) -> float:
    strong_kinds = {"scientific", "official", "fact_check"}
    if any(s.kind in strong_kinds for s in sources):
        return 90.0
    if any(s.credibility >= 0.85 for s in sources):
        return 75.0
    if sources:
        return 50.0
    return 0.0


def compute_rubric(
    sources: list[Source],
    evidence: list[Evidence],
    fact_check_hits: list[dict],
) -> RubricBreakdown:
    return RubricBreakdown(
        source_credibility=score_source_credibility(sources),
        source_diversity=score_source_diversity(sources),
        evidence_strength=score_evidence_strength(evidence, sources),
        fact_checker_consensus=score_fact_checker_consensus(fact_check_hits),
        media_authenticity=100.0,  # neutral in text-only MVP
        temporal_integrity=100.0,  # neutral in MVP
        original_source_traceability=score_original_source_traceability(sources),
    )


def weighted_score(rubric: RubricBreakdown) -> int:
    total = 0.0
    for field, weight in WEIGHTS.items():
        total += getattr(rubric, field) * weight
    return int(round(total / sum(WEIGHTS.values())))


def pick_verdict(
    score: int,
    fact_check_hits: list[dict],
    evidence: list[Evidence],
    sources: list[Source],
    satire_flag: bool,
) -> tuple[Verdict, float]:
    """Pick a verdict bucket + confidence from the score and signals."""
    if satire_flag:
        return Verdict.SATIRE, 0.9

    # Fact-checker majority (if strong) takes precedence over heuristics.
    if fact_check_hits:
        counter = Counter(h.get("rating_normalized", "UNKNOWN") for h in fact_check_hits)
        majority, count = counter.most_common(1)[0]
        if majority != "UNKNOWN" and count / sum(counter.values()) >= 0.6:
            try:
                return Verdict(majority), 0.85
            except ValueError:
                pass

    # Stance-based heuristic.
    supports = sum(1 for e in evidence if e.stance == Stance.SUPPORTS)
    refutes = sum(1 for e in evidence if e.stance == Stance.REFUTES)

    if supports + refutes < 2 and not sources:
        return Verdict.UNVERIFIABLE, 0.3

    if score >= 80 and supports > refutes:
        return Verdict.TRUE, 0.8
    if score >= 65 and supports >= refutes:
        return Verdict.MOSTLY_TRUE, 0.7
    if 45 <= score < 65:
        if refutes > supports:
            return Verdict.MISLEADING, 0.6
        return Verdict.MIXED, 0.55
    if score < 45 and refutes > supports:
        return Verdict.FALSE, 0.75
    if score < 45:
        return Verdict.MISLEADING, 0.55

    return Verdict.UNVERIFIABLE, 0.4


def confidence_from_signals(sources: list[Source], evidence: list[Evidence]) -> float:
    base = 0.2
    base += min(0.3, len(sources) * 0.04)
    base += min(0.3, len(evidence) * 0.03)
    if any(s.kind in {"fact_check", "scientific", "official"} for s in sources):
        base += 0.1
    return round(min(0.95, base), 2)
