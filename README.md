<div align="center">

# Veritas

**A multi-agent fact-checking chatbot.**
Drop in a claim, link, or social post → get a sourced verdict in seconds.

[![CI](https://github.com/Puneet00007/veritas/actions/workflows/ci.yml/badge.svg)](https://github.com/Puneet00007/veritas/actions/workflows/ci.yml)
![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![Next.js 15](https://img.shields.io/badge/next.js-15-black.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-MVP-orange.svg)

[Quickstart](#quickstart) · [Architecture](#architecture) · [Scoring](#scoring-rubric) · [Roadmap](docs/ROADMAP.md) · [Competitive analysis](docs/COMPETITIVE_ANALYSIS.md)

</div>

---

## What it does

Paste **anything** — text, news URL, social-media link — and Veritas:

1. **Extracts** the underlying factual claims.
2. **Researches** them in parallel across the open web, fact-checker registries, Reddit, and a built-in source-credibility table.
3. **Synthesizes** a verdict using a **transparent 7-component rubric** (no opaque trust badge).
4. **Red-teams** itself with a Critic agent that asks "what would have to be true for this to be wrong?".
5. **Streams** every step live to the UI via Server-Sent Events so a 12-second answer feels like 3.

```
TRUE  ·  MOSTLY_TRUE  ·  MIXED  ·  MISLEADING  ·  FALSE  ·  UNVERIFIABLE  ·  SATIRE
```

Every verdict ships with a numeric score (0–100), a confidence %, the cited evidence with stance tags (supports / refutes / context), per-source credibility, red flags, and an always-visible **"Why might I be wrong?"** counter-evidence tab.

---

## Why another fact-checker?

NewsGuard's January 2026 audit of the 11 leading chatbots found they repeat false claims **&gt;28% of the time** on controversial news. None of them are purpose-built. The deltas Veritas targets:

| Most chatbots | Veritas |
|---|---|
| Single LLM, opaque "trust me" answer | Multi-agent ensemble + adversarial Critic |
| Black-box confidence | Click any of 7 rubric components to see drivers |
| Skips the original source | Always tries to surface the primary doc / paper / filing |
| No social-origin tracing | Tracks who posted first, virality timeline, satire short-circuit |
| Hides counter-evidence | "Why might I be wrong?" tab on **every** verdict, including TRUE ones |

Full breakdown: [`docs/COMPETITIVE_ANALYSIS.md`](docs/COMPETITIVE_ANALYSIS.md).

---

## Architecture

A **supervisor orchestrator** fans out to 5 specialist sub-agents in parallel, collects results into a shared state, then runs **Synthesizer → Critic** before responding.

```
                                   ┌─────────────────────┐
   user input ──▶ Intake ──▶ Claim │  Web Research       │ ──┐
   (text/URL)       │      Extractor│  (Tavily + DDG)     │   │
                    │       │       ├─────────────────────┤   │
                    │       │       │  Fact-Check         │   │
                    │       └──────▶│  Registry (Google)  │ ──┤
                    │               ├─────────────────────┤   │
                    │               │  Reddit Signal      │ ──┼──▶ Synthesizer ──▶ Critic ──▶ Result
                    │               ├─────────────────────┤   │      (LLM)         (LLM)        │
                    │               │  Source             │   │                                 ▼
                    │               │  Credibility        │ ──┤                       ┌─────────────────┐
                    │               ├─────────────────────┤   │                       │ verdict + score │
                    └──────────────▶│  (satire short-     │   │                       │ rubric, evidence│
                                    │   circuit)          │ ──┘                       │ red flags, why-│
                                    └─────────────────────┘                           │ might-i-be-wrong│
                                                                                      └─────────────────┘
```

- **Backend** — Python 3.12 + FastAPI + asyncio supervisor (no LangGraph runtime yet — plain `asyncio.gather`).
- **Frontend** — Next.js 15 + React 19 + Tailwind. Renders a live event timeline as the pipeline runs.
- **Streaming** — `POST /api/check/stream` (SSE) emits `start → intake → claim_extraction → claims → fanout → agent_results → draft_verdict → critic → synthesizer → result`.
- **Offline mode** — with no API keys, `llm.py` falls back to a deterministic mock and external search returns empty. The pipeline still runs end-to-end so CI passes without secrets and the UI remains demo-able. An amber banner makes mock mode obvious.
- **Advanced features** — scaffolded as stubs in `backend/veritas/advanced/` (Socratic debate, claim genealogy, predictive misinfo, bias detection, blockchain audit, media forensics) and tracked in [`docs/ROADMAP.md`](docs/ROADMAP.md).

Full system design: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Quickstart

### Prerequisites

- Python **3.12+**, [uv](https://docs.astral.sh/uv/) (or `pip` + `venv`)
- Node **20+**, [pnpm](https://pnpm.io/) **9+**

### 1. Backend

```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -e .
cp .env.example .env        # optional — leave keys blank to run in mock mode
uvicorn veritas.main:app --port 8000 --reload
# → http://localhost:8000/healthz
```

### 2. Frontend

```bash
cd frontend
pnpm install
pnpm dev
# → http://localhost:3000
```

Open the UI, paste a claim or URL, and watch the timeline stream.

### 3. Try these inputs (no API keys required)

| Input | What it exercises | Expected |
|---|---|---|
| `The moon is made of cheese.` | Text intake + full streaming pipeline | 10 ordered SSE events, Unverifiable verdict (mock mode), all 5 tabs populated |
| `https://www.reuters.com/world/` | URL intake + TIER_1 credibility lookup | Source credibility = **95**, traceability = **75** |
| `https://www.theonion.com/` | Satire short-circuit | Dedicated `satire_detected` event, purple **Satire** badge |

### 4. Add real keys (optional)

Drop any of these into `backend/.env` to unlock the matching agent:

```bash
OPENAI_API_KEY=sk-...                  # claim extraction, synthesis, critic
TAVILY_API_KEY=tvly-...                # web research (free tier 1k calls/mo)
GOOGLE_FACT_CHECK_API_KEY=AIza...      # Google Fact Check Tools API (free)
```

Restart the backend; the amber mock banner disappears and real agents take over.

---

## API

### `GET /healthz`

```json
{ "ok": true, "llm_configured": false }
```

### `POST /api/check`

Synchronous. Body: `{ "input": "the claim or URL" }`. Returns the full `CheckResult` JSON.

### `POST /api/check/stream`

Same body. Returns an `text/event-stream` of `event: <name>\ndata: <json>\n\n` blocks (CRLF tolerant).

```bash
curl -N -X POST http://localhost:8000/api/check/stream \
  -H 'content-type: application/json' \
  -d '{"input":"https://www.reuters.com/world/"}'
```

### `CheckResult` (shortened)

```json
{
  "verdict": "MIXED",
  "legitimacy_score": 56,
  "confidence": 0.40,
  "tl_dr": "...",
  "claims": [{ "claim": "...", "verdict": "...", "evidence": [...] }],
  "sources":  [{ "id": 1, "url": "...", "publisher": "Reuters", "credibility": 0.95, "bias": "center" }],
  "evidence": [{ "source_id": 1, "quote": "...", "stance": "supports" }],
  "rubric": { "source_credibility": 95, "source_diversity": 20, "evidence_strength": 70, ... },
  "red_flags": ["majority_low_credibility_sources"],
  "why_might_i_be_wrong": "...",
  "critic_notes": "..."
}
```

---

## Scoring rubric

The legitimacy score (0–100) is a **transparent weighted sum**. The LLM explains the score; it does not pick it.

| Component | Weight | What it measures |
|---|---:|---|
| Source credibility | **×25** | Mean credibility of top 5 distinct sources (TIER_1 = 0.95, fact-checkers = 0.90, satire = 0.0, low-cred = 0.20) |
| Evidence strength | **×25** | Stance-weighted dominance — clear majority supports or refutes raises the score |
| Fact-checker consensus | **×15** | Agreement among indexed fact-checker rulings (Snopes / PolitiFact / Google Fact Check) |
| Source diversity | **×10** | Distinct domains contributing (5+ saturates) |
| Media authenticity | **×10** | `100 − max(deepfake, AI-generation)` (neutral=100 in MVP, populated in PR #2) |
| Original-source traceability | **×10** | Did we reach a primary doc (paper / filing / official) or only secondary outlets? |
| Temporal integrity | **×5** | Detects resurfaced old content & out-of-context quotes (neutral=100 in MVP) |

A satire-domain match short-circuits to verdict `SATIRE` regardless of the rubric.

---

## Project layout

```
veritas/
├── backend/
│   ├── veritas/
│   │   ├── main.py              # FastAPI app + /api/check[/stream]
│   │   ├── orchestrator.py      # supervisor; runs agents in parallel
│   │   ├── intake.py            # text vs URL detection + trafilatura fetch
│   │   ├── scoring.py           # 7-component rubric + verdict picker
│   │   ├── llm.py               # AsyncOpenAI + deterministic mock fallback
│   │   ├── credibility_data.py  # built-in domain → credibility table
│   │   ├── agents/              # claim_extractor, web_research, fact_check_registry,
│   │   │                        # reddit, source_credibility, synthesizer, critic
│   │   └── advanced/            # stubs: socratic_debate, claim_genealogy,
│   │                            # predictive_misinfo, bias_detection,
│   │                            # blockchain_audit, media_forensics
│   └── tests/                   # 15 unit + pipeline tests
├── frontend/
│   ├── app/page.tsx             # entry
│   ├── components/              # Chat, Timeline, VerdictCard,
│   │                            # EvidenceList, RubricBreakdown
│   └── lib/api.ts               # SSE streamCheck (CRLF-tolerant)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COMPETITIVE_ANALYSIS.md
│   └── ROADMAP.md
└── .github/workflows/ci.yml     # ruff + pytest + pnpm lint/typecheck/build
```

---

## Tests & lint

```bash
cd backend  && ruff check . && pytest -q                    # 15/15 pass
cd frontend && pnpm lint && pnpm typecheck && pnpm build    # clean
```

CI runs both jobs on every push.

---

## Roadmap

| | Theme |
|---|---|
| ✅ **PR #1** | MVP — text + URL, 5 agents, streaming UI, transparent rubric |
| ⏳ **PR #2** | Multi-modal — image (OCR + reverse search + Sightengine), audio (Whisper + AudD), short video; LLM stance classifier; multi-model ensemble |
| ⏳ **PR #3** | Interactive — Socratic Debate Mode, Claim Genealogy Tracker, narrative-cluster view, evidence-graph UI |
| ⏳ **PR #4** | Intelligence — predictive misinfo scoring, bias detection, regional fact-checker packs (India first), specialist agents |
| ⏳ **PR #5** | Trust + distribution — blockchain audit trail, public shareable verdict pages, Telegram bot, Chrome extension, Fly.io + Vercel deploy |

Full plan: [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

## Contributing

PRs welcome. Conventions:

- Match existing style (ruff for backend, ESLint+Prettier for frontend).
- Don't add new dependencies without a clear reason — Veritas optimizes for "works offline, in CI, without any keys".
- Don't commit secrets. The `.env` file is git-ignored; `backend/.env.example` is the template.

---

## License

MIT — see [`LICENSE`](LICENSE) (to be added in PR #2).

---

<sub>Built by [@Puneet00007](https://github.com/Puneet00007) with [Devin](https://devin.ai). Initial MVP shipped 2026-04-24.</sub>
