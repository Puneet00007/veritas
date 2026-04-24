"""Minimal LLM abstraction.

Uses OpenAI if OPENAI_API_KEY is set; otherwise a deterministic offline
mock that returns plausible-but-obviously-fake output. This lets the whole
pipeline run (and CI pass) without any external calls.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .config import settings


class LLM:
    def __init__(self) -> None:
        self._client: Any = None
        if settings.has_llm:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    @property
    def is_mock(self) -> bool:
        return self._client is None

    async def json(self, system: str, user: str, *, temperature: float = 0.2) -> dict:
        """Ask for a JSON object back."""
        if self._client is None:
            return _mock_json(system, user)
        resp = await self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        txt = resp.choices[0].message.content or "{}"
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            return {}

    async def text(self, system: str, user: str, *, temperature: float = 0.3) -> str:
        if self._client is None:
            return _mock_text(system, user)
        resp = await self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return (resp.choices[0].message.content or "").strip()


# ---------- mock helpers ----------

_CLAIM_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _hash01(s: str) -> float:
    h = int(hashlib.md5(s.encode("utf-8")).hexdigest()[:8], 16)
    return (h % 1000) / 1000.0


def _mock_json(system: str, user: str) -> dict:
    sys_l = system.lower()
    if "claim" in sys_l and "extract" in sys_l:
        sentences = [s.strip() for s in _CLAIM_SPLIT.split(user) if len(s.strip()) > 15][:5]
        return {
            "claims": [
                {"text": s, "who": None, "what": None, "when": None, "where": None}
                for s in sentences
            ]
            or [{"text": user.strip()[:300]}]
        }
    if "critic" in sys_l or "red-team" in sys_l or "red team" in sys_l:
        score = _hash01(user)
        return {
            "needs_another_round": score < 0.15,
            "issues": [] if score >= 0.15 else ["insufficient corroborating sources"],
            "notes": (
                "(mock critic) Evidence looks thin but verdict is defensible."
                if score >= 0.15
                else "(mock critic) Needs more sources before we finalize."
            ),
        }
    if "synthesize" in sys_l or "verdict" in sys_l:
        return {
            "tl_dr": "(mock) Insufficient real sources to judge — add OPENAI_API_KEY and a search key.",
            "why_might_i_be_wrong": "This is a mock LLM response used when no API keys are configured.",
        }
    return {}


def _mock_text(system: str, user: str) -> str:
    return "(mock) No LLM configured — set OPENAI_API_KEY to enable real synthesis."
