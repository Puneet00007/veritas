"""End-to-end pipeline test that runs with the mock LLM and with all
external network calls disabled (httpx.AsyncClient will just time out / fail
and the agents gracefully return []). Validates that even in full offline
mode the orchestrator produces a valid CheckResult.
"""

import asyncio
from unittest.mock import patch

import pytest

from veritas.orchestrator import Orchestrator
from veritas.schemas import CheckResult


@pytest.mark.asyncio
async def test_pipeline_offline_text_input():
    async def _empty_web(claims, per_claim=4):
        return []

    async def _empty_fc(claims):
        return []

    async def _empty_reddit(claims, per_claim=5):
        return []

    async def _empty_intake(raw_input):
        from veritas.schemas import ClaimPacket, InputKind

        return ClaimPacket(raw_input=raw_input, kind=InputKind.TEXT, normalized_text=raw_input)

    with (
        patch("veritas.orchestrator.build_packet", _empty_intake),
        patch("veritas.orchestrator.web_research.research", _empty_web),
        patch("veritas.orchestrator.fact_check_registry.lookup", _empty_fc),
        patch("veritas.orchestrator.reddit.signal", _empty_reddit),
    ):
        orch = Orchestrator()
        result = await orch.run("The earth is a flat disc held up by four elephants.")

    assert isinstance(result, CheckResult)
    # With zero external signals we should land on an UNVERIFIABLE / MISLEADING range.
    assert result.verdict.value in {"UNVERIFIABLE", "MISLEADING", "MIXED", "FALSE"}
    assert 0 <= result.legitimacy_score <= 100
    assert result.why_might_i_be_wrong
    assert result.rubric.source_credibility == 0.0
    assert isinstance(result.claims, list) and len(result.claims) >= 1


if __name__ == "__main__":
    asyncio.run(test_pipeline_offline_text_input())
