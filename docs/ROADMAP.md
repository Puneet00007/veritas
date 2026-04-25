# Veritas roadmap

This PR ships Week 1. Subsequent PRs will light up the advanced-feature stubs in `backend/veritas/advanced/`.

## ✅ PR #1 — MVP (this PR)
- FastAPI backend with async orchestrator (no LangGraph runtime yet — plain asyncio supervisor).
- Intake (text + URL), URL content fetch via trafilatura.
- Agents: claim extractor, web research (Tavily + DuckDuckGo fallback), Google Fact Check registry, Reddit signal, source credibility.
- Synthesizer + Critic/Red-Team.
- Transparent 7-component rubric.
- SSE streaming endpoint.
- Next.js 15 + Tailwind chat UI with live timeline, verdict card, evidence list, rubric breakdown, *"Why might I be wrong?"* tab, and critic notes.
- 15 unit + pipeline tests. Fully offline mode (mock LLM) for CI.

## PR #2 — Multi-modal + quality
- Image ingestion (OCR + reverse image search + Sightengine AI-gen/deepfake).
- Audio ingestion (Whisper + AudD).
- Short-video ingestion (yt-dlp → keyframes + audio).
- C2PA content credentials read.
- Proper LLM-based stance classifier (replaces lexical heuristic).
- Multi-model ensemble (OpenAI synth + Anthropic critic).

## PR #3 — Interactive features
- Socratic Debate Mode (`advanced/socratic_debate.py`).
- Claim Genealogy Tracker (`advanced/claim_genealogy.py`).
- Narrative-cluster view ("this tweet is 1 of 1,240 posts in 72h").
- Evidence-graph UI (interactive DAG).

## PR #4 — Intelligence
- Predictive Misinformation Scoring (`advanced/predictive_misinfo.py`).
- Bias Detection Engine (`advanced/bias_detection.py`).
- Regional fact-checker packs (India first — Alt News, Boom, Factly, Hindi/Tamil/Telugu/Bengali).
- Specialist agents (legal / scientific / financial / medical).

## PR #5 — Trust + distribution
- Blockchain audit trail (`advanced/blockchain_audit.py`).
- Public shareable verdict pages (SSR + OG tags + /v/[id]).
- Telegram bot adapter.
- Browser extension (Chrome MV3).

## PR #6 — Growth + monetization
- Stripe billing (Free / Pro / Team).
- Rate-limiting + auth (Supabase).
- "Watch this claim" subscriptions.
- WhatsApp Business API bot.
- Slack / Discord apps.

## PR #7 — Platform
- Community verification layer.
- Personal Media Diet Analyzer.
- Admin misinformation heatmap.
- Mobile apps (React Native or wrapped web).
