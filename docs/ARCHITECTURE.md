# Veritas — Multi-Agent Fact-Checking Chatbot
### Planning, Architecture & System Design (April 2026)

> Goal: user drops **anything** — a tweet/X post, Reddit thread, YouTube/TikTok link, news URL, plain text claim, image, audio clip, or short video — and gets back a **verdict** (True / Mostly True / Misleading / False / Unverifiable), a **legitimacy score (0–100)**, **confidence %**, **key evidence**, and **cited sources**. Powered by a supervisor orchestrating specialist sub-agents that each do deep research in parallel.

---

## 1. Product scope & UX

### 1.1 Input modalities (day 1)
| Modality | Examples | Handling |
|---|---|---|
| Plain text | "NASA confirmed aliens on Mars in April 2026" | Claim extraction → research |
| URL | x.com/..., reddit.com/..., youtube.com/..., news site | Fetch + extract content + treat content as claim |
| Image | screenshot of a tweet, news photo, meme | OCR + reverse image search + deepfake/AI-gen detection |
| Audio / music | voice note, song snippet, podcast clip | Whisper transcription + audio fingerprint (AudD/ACRCloud) + claim extraction |
| Short video | TikTok/Reel/Short | yt-dlp → frame sample + audio track → image & audio pipelines |

### 1.2 Output contract (strict JSON + a human-readable card)
```json
{
  "verdict": "MISLEADING",                    // TRUE | MOSTLY_TRUE | MIXED | MISLEADING | FALSE | UNVERIFIABLE | SATIRE
  "legitimacy_score": 38,                     // 0–100
  "confidence": 0.72,                         // 0–1, how sure the system is in its verdict
  "tl_dr": "The quote is real but stripped of context; the study cited does not support the claim.",
  "claims": [
    {
      "claim": "Study X shows Y causes Z",
      "verdict": "FALSE",
      "evidence": [ {source_id, quote, stance: "supports|refutes|context"} ]
    }
  ],
  "media_forensics": {
    "is_ai_generated": 0.91,
    "is_deepfake": 0.12,
    "reverse_image_hits": [ ... ],
    "earliest_known_appearance": "2024-03-11"
  },
  "sources": [
    { "id": 1, "url": "...", "title": "...", "publisher": "Reuters",
      "credibility": 0.92, "bias": "center", "date": "2026-04-19" }
  ],
  "red_flags": ["anonymous_source", "emotional_language", "out_of_context_quote"],
  "generated_at": "2026-04-24T14:46:00Z",
  "trace_id": "..."
}
```

---

## 2. High-level architecture

```
 ┌───────────────────────────────────────────────────────────────────┐
 │                        Client (Web / Telegram / WhatsApp)         │
 └──────────────────────────────┬────────────────────────────────────┘
                                │ HTTPS (SSE stream)
 ┌──────────────────────────────▼────────────────────────────────────┐
 │  API Gateway  (FastAPI)  — auth, rate limit, request/trace id     │
 └──────────────────────────────┬────────────────────────────────────┘
                                │
                     ┌──────────▼──────────┐
                     │  Intake & Router    │  (classify modality, normalize)
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │ Claim Extractor     │  (LLM → atomic checkable claims)
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │  SUPERVISOR AGENT   │  (LangGraph state machine)
                     └──────────┬──────────┘
          ┌─────────┬───────────┼───────────┬─────────┬──────────────┐
          ▼         ▼           ▼           ▼         ▼              ▼
     Web Research  Social    Fact-Check   Media     Source       Temporal/
       Agent      Platforms   Registry   Forensics Credibility   Context
                  Agent       Agent      Agent      Agent        Agent
          │         │           │           │         │              │
          └─────────┴───────────┼───────────┴─────────┴──────────────┘
                                ▼
                     ┌─────────────────────┐
                     │  Evidence Graph     │  (Neo4j / in-memory)
                     │  claims ↔ sources   │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │  Synthesizer /       │
                     │  Verdict Agent       │  (produces final JSON)
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │  Critic / Red-Team   │  (adversarial review, can veto)
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │  Response Formatter  │
                     └──────────┬──────────┘
                                ▼
                             to client
```

**Cross-cutting services:**
- **Cache** (Redis): canonicalized-URL → result, claim → result, image pHash → forensics result (TTL: news 1h, evergreen claims 7d)
- **Vector store** (pgvector or Qdrant): embedded past claims & retrieved evidence for RAG / dedup
- **Evidence graph** (Neo4j or in-memory NetworkX): nodes = claims, sources, entities, people; edges = supports / refutes / cites / published_by
- **Observability**: LangSmith or Langfuse for agent traces; OpenTelemetry for app metrics; Sentry for errors
- **Queue** (Celery/Redis or Dramatiq): heavy jobs (video download, deepfake check) run async with progress streamed via SSE

---

## 3. The agents (what each one does)

> Philosophy: each sub-agent is small, has a narrow tool belt, returns **structured** evidence (not prose), and writes into a shared **Evidence Graph**. The supervisor runs them in parallel where possible.

### 3.1 Intake & Router
- Detects modality (regex + `python-magic` + `urlparse`).
- If URL → calls Content Fetcher (below).
- Emits a normalized `ClaimPacket { text, urls[], images[], audio[], video[], metadata }`.

### 3.2 Content Fetcher (tool, not LLM)
- **News/articles** → `trafilatura` + Readability; fallback to headless Chrome (Playwright).
- **X/Twitter** → Nitter mirrors + `snscrape` fork (2026-maintained) + xAI API if key present.
- **Reddit** → **Reddit is hard in 2026** (API is paid/restricted). Use:
  1. Google site-search `site:reddit.com` via Tavily/Serper,
  2. `.json` suffix on public threads (still works with UA rotation),
  3. Pushshift mirror if available,
  4. Optional: authenticated PRAW with user's dev app if they provide creds.
- **YouTube/TikTok/Instagram** → `yt-dlp` → audio + sampled frames + description + comments.
- **Telegram public channels** → `Telethon`.
- **Bluesky/Mastodon/Threads/Truth Social** → their public APIs (all have one in 2026).

### 3.3 Claim Extractor (LLM)
- Decomposes the input into **atomic, checkable claims** with 5W metadata (who/what/when/where/why).
- Filters out opinions, jokes, and tautologies (important — cuts cost 40–60%).
- Flags satire sources (The Onion, Babylon Bee) early.

### 3.4 Web Research Agent
- Tools: **Tavily** (best default 2026), **Brave Search**, **SerpAPI/Serper** as fallbacks, **Exa/Metaphor** for neural search, **Wikipedia**, **Wikidata SPARQL** for entity facts.
- Strategy: generate 3–5 diverse queries per claim (HyDE-style) → dedupe → scrape top N → chunk → embed → re-rank with Cohere Rerank or BGE-reranker.
- Returns evidence snippets with stance tags (`supports` / `refutes` / `context`).

### 3.5 Social-Platforms Agent
- Specializes in finding the **original post** (not just articles about it), **who first posted it**, virality timeline, and community reaction.
- Sources: X, Reddit, Bluesky, Mastodon, Threads, TikTok, YouTube, Telegram, Truth Social, Farcaster.
- Uses: platform APIs where free, scraping where allowed, Tavily `include_domains` as fallback.
- Detects **coordinated inauthentic behavior** signals (burst posting, similar wording across accounts).

### 3.6 Fact-Check Registry Agent
- Queries known fact-checker corpora directly:
  - **Google Fact Check Claim Search API** (still available for read in 2026 even though ClaimReview write was phased out mid-2025),
  - **Snopes**, **PolitiFact**, **FactCheck.org**, **AP Fact Check**, **Reuters Fact Check**, **AFP Fact Check**, **Full Fact (UK)**, **Boom Live (India)**, **Alt News (India)**, **Chequeado (LatAm)**.
- Uses semantic search against a locally-indexed dump (refreshed nightly) for fast hits.

### 3.7 Media Forensics Agent
Runs only when image/video/audio present.
- **Reverse image search**: Google Lens (SerpAPI), Bing Visual Search, TinEye, Yandex.
- **Image pHash / aHash** to cluster near-duplicates and find earliest appearance.
- **AI-generation detection**: **Sightengine** (good default, cheap), **Hive Moderation**, **Reality Defender** (enterprise).
- **Deepfake detection** (face swap specifically): Sightengine deepfake model, Hive deepfake.
- **EXIF + C2PA content credentials** check (growing adoption in 2026).
- **Audio**: Whisper-v3 for transcription; **AudD** / **ACRCloud** for music fingerprinting; AI-voice detection via Sightengine audio or Pindrop.
- **Video**: sample N keyframes → run image pipeline; run audio pipeline on the track.

### 3.8 Source Credibility Agent
- Per-source scoring combining:
  - **Media Bias/Fact Check** (MBFC) tier,
  - **Ad Fontes Media** bias chart (via API),
  - **NewsGuard** if available,
  - Domain age & WHOIS,
  - HTTPS / known-misinformation blocklists (e.g., Iffy.news),
  - Wikipedia entry on the outlet.
- Produces `(credibility 0–1, bias: left|center-left|center|center-right|right|unknown, type: news|blog|satire|state_media|social)`.

### 3.9 Temporal / Context Agent
- Detects **resurfaced old content** (huge misinformation vector): compares image earliest-appearance, article publish date, claimed-event date.
- Flags "stripped context" (quote is real but said in a different setting) by searching the exact phrase.
- Cross-references timelines against Wikipedia "current events" and Wikidata.

### 3.10 Synthesizer / Verdict Agent
- Reads the Evidence Graph.
- Applies a deterministic scoring rubric (see §4) **plus** an LLM rationale.
- Produces the final JSON contract.

### 3.11 Critic / Red-Team Agent
- Adversarially challenges the verdict: "What would it take for this to be wrong?"
- If it finds a plausible counter-argument not addressed by evidence, it **kicks the case back** to the supervisor for one more research loop (max 2 iterations).
- Drastically reduces hallucinated confidence.

---

## 4. Scoring rubric (legitimacy score 0–100)

Weighted, transparent, **shown to the user**:

| Component | Weight | How it's computed |
|---|---|---|
| Source credibility | 25 | Mean credibility of top-5 distinct corroborating sources |
| Source diversity | 10 | # of independent outlets (not syndications) corroborating |
| Evidence strength | 25 | stance-weighted: +supports, −refutes, gated by source credibility |
| Fact-checker consensus | 15 | Matches in Snopes/PolitiFact/etc. |
| Media authenticity | 10 | 100 − max(deepfake_prob, ai_gen_prob)·100, if media present |
| Temporal integrity | 5 | Penalty if resurfaced/out-of-date |
| Original-source traceability | 10 | Can we reach the primary source (paper, court doc, official statement)? |

**Confidence** is separate: a function of evidence quantity, agreement between agents, and Critic's residual doubt.

---

## 5. Data flow (detailed, single request)

1. User POSTs `/check` with payload (text/url/file).
2. Gateway assigns `trace_id`, streams SSE back.
3. Intake normalizes → `ClaimPacket`.
4. Cache check (canonical URL, text hash, image pHash). **Hit → return in <200 ms.**
5. Claim Extractor splits into atomic claims.
6. Supervisor fans out:
   - Web Research (parallel per claim),
   - Social Platforms,
   - Fact-Check Registry,
   - Media Forensics (if media),
   - Source Credibility (reacts as sources arrive).
7. Each agent writes into the Evidence Graph; the frontend sees live progress: *"Found 12 sources… checking Snopes… running deepfake detector…"*.
8. Synthesizer computes score + verdict.
9. Critic reviews; may trigger **one** extra research round.
10. Formatter renders the card + JSON; result is cached.
11. Telemetry logged to LangSmith/Langfuse.

**Latency targets:** p50 < 12 s for text/URL, < 25 s with media; p95 < 45 s. Streaming UI makes this feel faster.

---

## 6. Tech stack (recommendation, April 2026)

| Layer | Choice | Why |
|---|---|---|
| Language | **Python 3.12** | Best ecosystem for scraping + ML tooling |
| API | **FastAPI** + SSE | Async, typed, easy |
| Orchestration | **LangGraph** | Deterministic, checkpointable, best debuggability in 2026; supervisor pattern is a first-class citizen |
| LLMs | **GPT-5 / GPT-4.1** primary, **Claude 4 Sonnet** for Critic (diversity reduces shared blind spots), **Gemini 2.5** fallback with native Google Search grounding | Router picks per task by cost/quality |
| Embeddings | **text-embedding-3-large** or **Voyage-3** | Strong retrieval |
| Vector DB | **Qdrant** (self-host) or **pgvector** | Cheap, good enough |
| Graph | **Neo4j Community** or in-process NetworkX for MVP | |
| Cache / Queue | **Redis** + **Dramatiq** | |
| Search | **Tavily** (primary), **Brave**, **Serper**, **Exa** | Multiple for resilience |
| Scraping | **Playwright** + **trafilatura** + **yt-dlp** + **snscrape** + **Telethon** | |
| Media forensics | **Sightengine** (start here — one API covers AI-image, deepfake, AI-audio, AI-video), add **Hive** for redundancy | |
| Audio ID | **AudD** or **ACRCloud** | |
| Transcription | **Whisper v3** (local) or **Deepgram Nova-3** | |
| Observability | **Langfuse** (OSS, self-hostable) | Cheaper than LangSmith at scale |
| Frontend | **Next.js 15** + shadcn/ui + streaming chat | |
| Deploy | Backend → Fly.io or Railway; Frontend → Vercel; Heavy workers → Modal or RunPod if GPU needed for Whisper | |

> If you want open-source-only, swap LLMs for **Llama-3.3-70B / Qwen-2.5-72B via Together.ai**, search for **SearxNG**, forensics for **DeepSafe** or in-house CLIP-based detectors.

---

## 7. Features beyond the core MVP

- **Browser extension** ("Check this tweet") — one-click on any URL.
- **Telegram / WhatsApp / Discord bots** — forward a message, get a verdict. This is where most misinfo actually spreads.
- **"Watch this claim"** — user subscribes; we notify them if new evidence materially changes the verdict.
- **Community notes-style voting** on verdicts (with reputation).
- **Explainable view**: clickable evidence graph with highlighted quotes from each source.
- **Source-substitution awareness**: detects when a legit image is paired with a fabricated caption.
- **Multilingual**: accept & respond in user's language; fact-check in the source language first.
- **"Why might I be wrong?"** tab — always surfaces the strongest counter-evidence, even when verdict is TRUE. Builds trust.
- **Local/regional specialists**: plug in India-specific (Alt News/Boom), LatAm (Chequeado), etc.
- **Safety rails**: refuse to opine on unfalsifiable claims (religion, ideology); clearly label as "OPINION / UNFALSIFIABLE".
- **Audit log export** for journalists/researchers.
- **Rate-limited free tier + paid API** for monetization.
- **Abuse handling**: hash-blocklist CSAM / extremist content BEFORE any agent processes it.

---

## 8. Cost model (rough, per check, 2026 pricing)

| Item | Cost/check |
|---|---|
| LLM calls (supervisor + 6 sub-agents, avg 30k input / 3k output tokens total) | $0.04–$0.10 |
| Search APIs (Tavily 5–10 calls) | $0.01–$0.03 |
| Media forensics (Sightengine) | $0.005 per image, $0.02 per 10s audio |
| Whisper (self-hosted GPU) | ~$0 marginal |
| Infra amortized | $0.005 |
| **Total** | **~$0.06 (text) / $0.12 (with media)** |

Caching aggressively on viral content brings the effective cost per *unique user request* down ~5×.

---

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| **LLM hallucinates citations** | Every cited URL must actually appear in the retrieved evidence corpus; Critic verifies quotes exist in the source text. |
| **Over-confident FALSE on emerging news** | Time-decay: claims < 6h old capped at MIXED/UNVERIFIABLE unless multiple tier-1 outlets agree. |
| **Adversarial prompt injection via scraped content** | Strip/escape scraped HTML, sandbox agent prompts, never let retrieved text issue instructions (use a "content-only" role). |
| **Deepfakes passing detection** | Ensemble two vendors; require corroborating evidence beyond just media forensics. |
| **Reddit/X API restrictions** | Multi-source fallbacks (search engines, mirrors, user-provided API keys). |
| **Cost explosion on viral claim** | Redis cache on canonical forms (normalized URL, text hash, image pHash) + semantic-dedup on similar claims. |
| **Bias in fact-checkers themselves** | Show *which* fact-checkers agreed/disagreed; never treat any single outlet as ground truth. |
| **Legal (defamation, platform TOS)** | Always cite; show evidence; label as "automated analysis, not a final determination"; respect robots.txt & ToS; offer source removal on request. |

---

## 10. Roadmap

### **MVP (Week 1–2)** — prove the core loop
- FastAPI backend + minimal Next.js chat UI.
- Text + URL input only.
- LangGraph: Intake → Claim Extractor → Web Research → Fact-Check Registry → Source Credibility → Synthesizer.
- Tavily + Google Fact Check API + MBFC list.
- Redis cache, Langfuse traces.
- Deploy to Fly.io + Vercel.

### **v0.2 (Week 3–4)** — images + social
- Image ingestion: OCR (Tesseract) + reverse image search (SerpAPI Google Lens) + Sightengine AI-gen.
- Social Platforms Agent (X via Nitter, Reddit via `.json`, YouTube via yt-dlp).
- Critic agent.
- Evidence graph view in UI.

### **v0.3 (Week 5–6)** — audio, video, browser extension
- Whisper transcription, yt-dlp for short video, audio fingerprinting.
- Chrome extension (context-menu "Check with Veritas").
- Telegram bot.

### **v1.0 (Week 7–8)** — polish + monetize
- "Watch this claim" subscriptions.
- Multilingual.
- Paid API tier + rate limiting.
- Community notes beta.

---

## 11. Open questions for you

1. **Deployment target** first: web chat only, or also Telegram/WhatsApp from day 1?
2. **LLM budget**: OK to use GPT-5 + Claude 4 + Gemini (best quality, ~$0.10/check) or do you want open-source-only (~$0.02/check, lower quality)?
3. **Media on day 1 or day 14?** Images add a week but huge value.
4. **Repo**: new repo `veritas` under your GitHub `Puneet00007`?
5. **Secrets available**: do you already have OpenAI/Anthropic/Tavily/Sightengine keys, or should I request them?

Tell me the answers (or say **"you pick, start building"**) and I'll move to implementation.
