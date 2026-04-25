from veritas.schemas import Evidence, RubricBreakdown, Source, Stance, Verdict
from veritas.scoring import (
    compute_rubric,
    confidence_from_signals,
    pick_verdict,
    weighted_score,
)


def _source(sid: int, domain: str, cred: float, kind: str = "news") -> Source:
    return Source(
        id=sid,
        url=f"https://{domain}/x",
        title="t",
        publisher=domain,
        domain=domain,
        credibility=cred,
        kind=kind,
    )


def test_weighted_score_monotonic():
    rubric_low = RubricBreakdown(
        source_credibility=10,
        source_diversity=10,
        evidence_strength=10,
        fact_checker_consensus=10,
        media_authenticity=10,
        temporal_integrity=10,
        original_source_traceability=10,
    )
    rubric_high = RubricBreakdown(
        source_credibility=95,
        source_diversity=95,
        evidence_strength=95,
        fact_checker_consensus=95,
        media_authenticity=95,
        temporal_integrity=95,
        original_source_traceability=95,
    )
    assert weighted_score(rubric_low) < weighted_score(rubric_high)


def test_rubric_handles_empty():
    rubric = compute_rubric([], [], [])
    assert rubric.source_credibility == 0.0
    assert rubric.fact_checker_consensus == 50.0


def test_pick_verdict_false_on_refutes():
    sources = [_source(1, "reuters.com", 0.95, kind="news"), _source(2, "snopes.com", 0.90, kind="fact_check")]
    evidence = [
        Evidence(source_id=1, quote="x", stance=Stance.REFUTES),
        Evidence(source_id=2, quote="y", stance=Stance.REFUTES),
    ]
    fc_hits = [
        {"rating_normalized": "FALSE"},
        {"rating_normalized": "FALSE"},
    ]
    rubric = compute_rubric(sources, evidence, fc_hits)
    score = weighted_score(rubric)
    verdict, _ = pick_verdict(score, fc_hits, evidence, sources, False)
    assert verdict == Verdict.FALSE


def test_satire_short_circuit():
    verdict, conf = pick_verdict(50, [], [], [], satire_flag=True)
    assert verdict == Verdict.SATIRE
    assert conf >= 0.8


def test_confidence_grows_with_signals():
    few_src = [_source(1, "a.com", 0.5)]
    many_src = [_source(i, f"d{i}.com", 0.8, kind="fact_check") for i in range(1, 8)]
    few_ev = [Evidence(source_id=1, quote="q", stance=Stance.CONTEXT)]
    many_ev = [Evidence(source_id=i, quote="q", stance=Stance.SUPPORTS) for i in range(1, 8)]
    assert confidence_from_signals(few_src, few_ev) < confidence_from_signals(many_src, many_ev)
