# Veritas — local dev & testing

## Run end-to-end locally

Two processes, two ports.

```bash
# Backend (FastAPI + SSE)
cd backend
uv venv && source .venv/bin/activate
uv pip install -e .
uvicorn veritas.main:app --port 8000

# Frontend (Next.js 15)
cd frontend
pnpm install
pnpm dev          # http://localhost:3000
```

Frontend reads `NEXT_PUBLIC_BACKEND_URL` (defaults to `http://localhost:8000`). Backend `GET /healthz` returns `{ ok: true, llm_configured: <bool> }`.

## Mock-LLM mode (no keys = pipeline still runs)

With no `OPENAI_API_KEY` / `TAVILY_API_KEY` / `GOOGLE_FACT_CHECK_API_KEY` set, the backend runs in **mock mode**: deterministic fake JSON from `veritas/llm.py` + empty external search results. The full streaming pipeline still completes, satire short-circuit still fires, source-credibility lookup still works (it's a static table in `credibility_data.py`). The frontend shows an amber "Running without an LLM / search API key" banner whenever the result has `extras.llm_mock === true`.

This means **CI passes without secrets** and we can always do structural E2E testing locally. To test verdict *accuracy*, drop keys into `backend/.env`.

## SSE CRLF gotcha (don't re-introduce)

`sse_starlette` (the backend SSE library) emits `\r\n\r\n` between events, not `\n\n`. The frontend SSE parser in `frontend/lib/api.ts` MUST accept both — split the buffer on regex `/\r?\n\r?\n/` and split lines on `/\r?\n/`. A pure `"\n\n"`-string split silently drops every event and `streamCheck` returns `null`. Symptom: only the user's message bubble renders, no Timeline, no VerdictCard, but the Network tab shows a 200 OK SSE response with all events present.

## Canonical smoke tests for E2E

Three inputs cover the major code paths and need no API keys:

1. `The moon is made of cheese.` — exercises text intake + full streaming pipeline. Expect `kind=text`, ~10 ordered events (start → intake → claim_extraction → claims → fanout → agent_results → draft_verdict → critic → synthesizer → result), Unverifiable verdict in mock mode, all 5 tabs (Evidence / Rubric / Claims / Why might I be wrong? / Critic) populated.
2. `https://www.reuters.com/world/` — exercises URL intake + trafilatura fetch + TIER_1 credibility lookup. Expect Rubric → Source credibility = **95**, Original source traceability = **75**.
3. `https://www.theonion.com/` — exercises satire short-circuit. Expect a dedicated `satire_detected` event in the Timeline and a purple **Satire** verdict badge (not MIXED, not UNVERIFIABLE).

A broken implementation will visibly fail at least one of these.

## Recording E2E tests

Maximize the browser before recording (window managers like the default one tile to half-screen on Super+Up):

```bash
wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz
```

Then `record_start` → `record_annotate` with `setup` / `test_start` / `assertion` per the standard recording skill.

## Tests & lint

```bash
cd backend && ruff check . && pytest -q       # 15 tests, must stay green
cd frontend && pnpm lint && pnpm typecheck && pnpm build
```

CI runs both jobs in `.github/workflows/ci.yml`.
