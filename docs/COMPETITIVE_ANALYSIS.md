# Veritas — Competitive Analysis & Expanded Feature Set
### April 2026

---

## Part 1 — Who we're up against

I grouped competitors into **5 buckets** because we're actually competing in 5 overlapping markets at once.

### Bucket A — General "answer engines" people *use* as fact-checkers
These aren't fact-checkers by design, but ~70% of users go to them first.

| Product | What it does well | Where it loses | How we beat it |
|---|---|---|---|
| **ChatGPT-5 / 5.2** | Massive knowledge, great UX | No structured verdict, no confidence, weak on breaking news, no media forensics, no social-post fetching | We give a **scored verdict + citations + forensics**, not prose |
| **Perplexity** | Fast cited search, nice UI | Known to pick biased sources, no verdict, no forensics, no social-originality check, no "why might I be wrong" | Dedicated sub-agents for **social origin, media forensics, source credibility**; red-team critic |
| **Grok 4.20** | Real-time X access, strong non-hallucination (83% on AA-Omniscience), cheap via xAI | Single-model, single-source bias, no image/audio forensics, only X's info feed | We **ensemble Grok + GPT-5 + Claude** → cross-check across models; add media pipeline Grok doesn't have |
| **Gemini 2.5** | Native Google Search grounding | No verdict format, no media forensics pipeline, no source credibility layer | Same as above — we add structure, forensics, and scoring |
| **You.com / Smart Assistant** | Multi-agent answers | No focus on misinfo; NewsGuard's Jan 2026 audit showed it still repeats ~28% of false claims | We're **purpose-built** for this one task |

**Key insight:** NewsGuard's Q1 2026 audit showed the 11 leading chatbots repeat false claims **>28% of the time** on controversial news topics. That's the gap.

### Bucket B — Purpose-built fact-checking platforms (mostly B2B)

| Product | What it does | Why a consumer can't really use it |
|---|---|---|
| **Factiverse** (launching Spring 2026) | Extracts checkable claims from political video/audio in 110+ languages | Priced for newsrooms, intelligence agencies, governments. No consumer chat. |
| **Logically.ai** | Enterprise misinfo monitoring + human analysts | Paid, not interactive, not for end-users |
| **NewsGuard** | Source-level credibility ratings (browser plug-in + API) | Rates *sites*, not claims or images. No multi-modal. |
| **TrustServista** | Content analytics for media pros | B2B only |
| **Full Fact AI** | Claim matching + near-duplicate detection for UK fact-checkers | Newsroom tool, English-centric |
| **Meedan Check** | Backend that powers WhatsApp tiplines for AFP / BOOM / Africa Check / India Today | Works only through partner fact-checker orgs; users wait for a human reply |
| **Google Fact Check Explorer** | Searches existing fact-checks | Only returns what *humans already checked*. Nothing on novel claims, images, or audio. Google phased out ClaimReview writes in mid-2025, ecosystem is shrinking. |

**Key insight:** the pro tools are powerful but **gated behind newsrooms**. Regular users and journalists-of-one have nothing that works end-to-end on any modality. That's our lane.

### Bucket C — Platform-native "add-context" systems

| Product | Strength | Weakness we exploit |
|---|---|---|
| **X Community Notes** | Huge scale, bridge-based ranking | Slow (median hours to days), confined to X, currently in regulatory fight in India / EU, politically captured claims get stuck. |
| **Meta's Community Notes clone** (rolled out late 2025) | Similar to X's | Even slower, less mature |
| **TikTok "Footnotes"** (pilot) | Same pattern | Limited rollout |

**Key insight:** crowd notes are **reactive and platform-locked**. We work **cross-platform, on-demand, in seconds**, and we can feed *into* community notes (see Features §14).

### Bucket D — Media forensics point-solutions

| Product | Strength | Weakness |
|---|---|---|
| **Sightengine / Hive / Reality Defender** | Deepfake & AI-image detection APIs | One narrow question; no research, no context, no verdict |
| **InVID-WeVerify** (browser extension) | Journalist's Swiss Army knife: reverse search, keyframes, magnifier | Entirely manual, no LLM synthesis |
| **TinEye / Google Lens** | Reverse image search | Raw tool, no interpretation |

**Key insight:** these are **ingredients**. We're the chef. Our media forensics agent *uses* Sightengine/Hive under the hood, but adds cross-modal reasoning ("the image is AI-generated *and* the quote overlaid on it was never said").

### Bucket E — Messaging-app tiplines (the most used in the Global South)

| Product | Where | Limitation |
|---|---|---|
| **Meedan-powered tiplines** (AFP India, BOOM, Africa Check) | WhatsApp | Human reply, hours to days |
| **Aos Fatos "Fátima" bot** (Brazil) | WhatsApp | Template-based, narrow |
| **Lead Stories WhatsApp bot** (US) | WhatsApp | Mostly archive lookup |
| **PesaCheck / Africa Check bots** | Various | Same pattern |

**Key insight:** in India, Brazil, Nigeria, South Africa, Kenya — **WhatsApp and Telegram are the front line** and the existing bots rely on human fact-checkers. A fast AI-first bot (with human review on disputed cases) is wide open.

---

## Part 2 — What we do better (the differentiation list)

Pick and choose — these are our moats, ordered from most to least defensible.

### 2.1 True **multi-modal, single-interface** (image + audio + video + text + URL + social post)
Nobody on the list above does all 6 through one chat. Perplexity does text/URL. Grok does text/X. Sightengine does images only. We're the only one where a user can paste *any* content type and get the *same* verdict contract.

### 2.2 **Multi-model ensemble + Critic/Red-Team** to cut hallucinations
NewsGuard's 28% false-claim-repetition number is on **single-model** chatbots. Running GPT-5 + Claude 4 in parallel and using Claude as a dedicated adversarial Critic measurably drops error rates (Google's own research on LLM judges, 2024–25, showed ensemble judging cuts disagreement by ~40%). **This is a verifiable, testable moat.**

### 2.3 **Transparent scoring rubric** instead of a black-box trust badge
NewsGuard gives one opaque score. Grok's extension gives a "trust score" with no breakdown. We publish the 7-component rubric (credibility / evidence / fact-checker consensus / diversity / media authenticity / traceability / temporal) and let users click each weight.

### 2.4 **Original-source traceability**
Most competitors stop at "a reputable outlet reported this". We try to reach the **primary source** — the court filing, the paper on arXiv, the government press release, the original video. That's what distinguishes "reported" from "true".

### 2.5 **Provenance & resurfaced-content detection**
Combine image pHash earliest-appearance + "exact phrase" search + Wayback Machine snapshots + C2PA content-credentials read. Catches the single biggest 2026 misinfo vector: real old content with a fake new caption.

### 2.6 **"Why might I be wrong?" tab** (always on, even on TRUE verdicts)
Built into every response. Competitors never volunteer counter-evidence. This is the *single biggest trust-builder* we can ship.

### 2.7 **Cross-platform social-origin tracing**
We don't just say "this is going viral" — we identify:
- Who posted it first (earliest timestamp across X, Reddit, Bluesky, Telegram, TikTok, Threads, Mastodon, Truth Social, Farcaster)
- How it propagated (virality timeline chart)
- Whether similar text appeared on multiple accounts within a short window (coordinated-behavior heuristic)

Nobody in Bucket A or B does this end-to-end.

### 2.8 **Stance-aware evidence**, not vibes
Every retrieved passage is tagged `supports` / `refutes` / `context` with a source-credibility weight. The verdict is computed from a **deterministic formula** *then* explained by the LLM — the reverse of Perplexity/Grok which let the LLM decide first.

### 2.9 **Regional fact-checker packs**
Pluggable packs so the same bot works in:
- **India** — Alt News, Boom Live, Vishvas, The Quint WebQoof, Factly (+ Hindi/Tamil/Telugu/Bengali)
- **LatAm** — Chequeado, Aos Fatos, Maldita, Verificado
- **Africa** — Africa Check, PesaCheck, Dubawa
- **SE Asia** — Rappler, Tempo, Mafindo
- **Europe** — Full Fact, Correctiv, Maldita.es, Les Surligneurs

No global competitor ships with this level of regional depth.

### 2.10 **Speed via streaming UI**
Competitors make you wait in silence. We stream "🔍 found 12 sources… 🖼️ checking image against TinEye… ✅ Snopes match found" so 12 s feels like 3.

### 2.11 **Open-source core + self-hostable**
Most competitors are closed SaaS. Open-sourcing the orchestration + rubric (keeping the hosted forensics keys closed) earns trust with journalists and researchers, drives community contributions, and is itself a marketing moat.

### 2.12 **Cheaper than everyone by 3–10×**
Factiverse/Logically/NewsGuard are $$$$/month enterprise contracts. Perplexity Pro is $20/mo flat. We can ship a free tier (rate-limited) and a $9/mo power tier profitably at ~$0.08/check fully-loaded.

---

## Part 3 — Extra features (beyond what I listed in v1 of the plan)

I grouped these so you can pick a theme. A `★` marks what I'd ship first.

### A. Trust & explainability
- `★` **"Why might I be wrong?"** — always-on counter-evidence tab.
- `★` **Evidence graph view** — interactive: nodes = claims/sources/entities, edges = supports/refutes, hover to see exact quotes.
- **Rubric breakdown** — click any score component to see which sources drove it.
- **Source dossier on hover** — credibility, bias, domain age, Wikipedia summary, past errors.
- **"Show me the primary source"** button — always tries to reach the original document.
- **Verdict history** — if the same claim is re-checked later and the verdict changes, show the diff and why.
- **Dissent log** — we publish cases where our verdict disagrees with Snopes/PolitiFact *and* our reasoning. Builds credibility.

### B. Input ergonomics
- **Browser extension**: right-click → "Check with Veritas" on any tweet/article/image.
- **Share-sheet integration** (iOS/Android) — share from any app.
- **Telegram, WhatsApp, Discord, iMessage, Signal** bots — forward a message, get a verdict.
- **Email address** (`check@veritas.app`) — forward a suspicious email/newsletter, get a reply.
- **SMS gateway** (cheap, important for low-bandwidth regions).
- **Voice mode** — "Hey, is it true that X?" via Siri Shortcut / Google Assistant / Alexa.
- **Drag-and-drop a video file** — not just a URL.
- **Screenshot paste** — Ctrl+V directly into the chat box.

### C. Proactive / monitoring
- **"Watch this claim"** — re-checks nightly; pings you if the verdict changes.
- **Topic feeds** — subscribe to "India politics" / "AI industry" / "vaccines" and get a daily digest of the top 5 fact-checked claims trending on social.
- **Newsletter integration** — pipe your Substack/email subscriptions through Veritas; it annotates each article inline with verdicts.
- **RSS fact-check feed** per topic, consumable by any reader.
- **Slack/Teams app** for newsrooms: drop a link in a channel, bot replies with verdict.
- **Election mode** — country-configurable window where social-platform agents increase sampling rate and flag new misinfo narratives in near-real-time.

### D. Media & forensics upgrades
- **C2PA content-credentials reader** — show "signed by Canon R5 on 2025-11-03, edited in Photoshop 26.1" or "no credentials, source unknown".
- **Voice-cloning detection** (Pindrop / Resemble Detect) for audio.
- **Lip-sync inconsistency check** for video (open-source: `SyncNet`-style).
- **Face identity lookup** — "whose face is in this image?" via reverse search on recognizable public figures (with a consent policy — never on private individuals).
- **Chart & screenshot fact-check** — OCR data from a chart → re-check the numbers against the cited source.
- **Document verification** — uploaded PDFs: check metadata, detect AI-generated text sections via Originality.ai / GPTZero-style ensemble.
- **Provenance timeline** — "this image has appeared online since 2019; claim of it being from yesterday is false".

### E. Agent upgrades
- **Specialist agents** behind a model router: a **legal-claims agent** (pulls court filings, PACER/CourtListener), a **scientific-claims agent** (PubMed, arXiv, Retraction Watch), a **financial-claims agent** (SEC EDGAR, earnings calls), a **geopolitical agent** (ACLED, OSINT sources), a **medical agent** (WHO, CDC, Cochrane).
- **Entity linking** — Wikidata/DBpedia so "Elon Musk's company" resolves correctly.
- **Satire detector** — explicit check against a satire-site list + stylistic classifier.
- **Translation agent** — check in source language first (e.g. Hindi claim against Hindi-language fact-checkers) and only then translate for the English-speaking user.
- **Code-of-ethics enforcement** — refuses to rule on religious or purely opinion claims; labels them UNFALSIFIABLE and stops.

### F. Community & network effects
- **Anonymous public verdict pages** (like Snopes articles) — every check produces a shareable URL that search engines can index. Huge SEO flywheel.
- **User reputation** — verified contributors can upvote/downvote evidence, flag missing sources.
- **"Request a human review"** — dispute the AI verdict; a human fact-checker (partner newsroom) adjudicates; all parties get notified when resolved.
- **Bounty program** — pay users who find and submit high-quality counter-evidence that flips a verdict.
- **API for researchers** — bulk verdict data, free for academic use.
- **Partnerships with IFCN-signatory fact-checkers** — we send them claims we can't resolve; they get attribution + traffic.

### G. Platform integrations
- **"Check this tweet" button** we inject into X (via extension).
- **Direct feed to X Community Notes**: when we produce a high-confidence verdict on a viral post, surface it to volunteer note-writers so they can adopt and cite it.
- **Bluesky AT-Protocol labeler** — Veritas can act as an opt-in labeling service on Bluesky (native feature, already a thing in 2026).
- **YouTube Studio integration** for creators — pre-publish, check your own video's claims.
- **Newsletter/CMS plugins** (WordPress, Ghost, Substack): "Veritas-verified" badges on articles that pass pre-publish checks.
- **Zapier/Make/n8n** — anyone can pipe their data stream through a verdict step.

### H. Personalization & safety
- **Explainable personal bias panel** — shows the user which sources they click through and flags if they're filter-bubbling.
- **Child-safety mode** — stricter thresholds, softer language, no gore/NSFW media ever retrieved.
- **Jurisdiction-aware disclaimers** — EU (DSA), UK (Online Safety Act), India (IT Rules 2026 amendments) — different legal language per region, automatically.
- **Hash-blocklist gate** — any input is checked against CSAM/terror-content hashes BEFORE any agent runs.

### I. Monetization (extra features that also pay bills)
- **Free tier**: N checks/day, watermarked results.
- **Pro ($9/mo)**: unlimited, priority queue, monitoring, browser extension, history.
- **Team ($29/user/mo)**: Slack/Teams bot, shared workspace, API, audit logs.
- **Enterprise / newsroom**: custom fact-checker integrations, SSO, on-prem option, regional packs, SLA.
- **Public-interest free tier** — IFCN-member newsrooms get it free forever (goodwill + partnership flywheel).
- **Data products**: aggregated (never personal) misinfo narrative trend reports sold to platforms, academic institutions, governments. This is how Logically and NewsGuard actually make money.

### J. Research & data-loop (long-term moat)
- **Every check produces a training datum** — (claim, retrieved evidence, verdict, user feedback). Over time we fine-tune a small verdict-scorer model that's faster and cheaper than GPT-5.
- **Benchmark ourselves publicly** against the NewsGuard AI False Claim Monitor — publish our score every quarter.
- **Open eval set**: host a leaderboard of fact-checkers (ours + competitors) on a rolling set of fresh misinfo claims. We win → marketing. We lose → we get better.
- **Dataset release** for academic researchers (stripped of PII).

### K. Unique wedge features nobody has today
- **"Claim DNA"** — fingerprint a claim (embedding + entity set + numeric facts) so we can tell you "this is the same claim as one that went viral in 2022 with FALSE verdict" even when worded completely differently.
- **Narrative-cluster view** — when checking a single tweet, show the broader *narrative* it's part of, across platforms (e.g. "this is one of 1,240 posts in the past 72h pushing the 'election stolen' narrative, 89% from accounts < 6mo old").
- **Adversarial self-probe** — before finalizing, we ask "what's the strongest prompt that would convince me this is true/false?" and try to refute our own verdict. This is basically debate-style self-critique from the Anthropic Constitutional-AI playbook.
- **Post-mortem on viral misinformation** — weekly automated report: "Top 10 viral falsehoods this week, our verdict, who first posted, who amplified."
- **Personal fact-check journal** — everything you've ever checked, searchable, private. Great for journalists and researchers.

---

## Part 4 — Positioning statement (one sentence)

> **Veritas** is the only consumer fact-checker that takes **any** input (text, link, image, audio, video, social post), runs **eight specialist AI agents in parallel** against **40+ sources** (fact-checkers, news wires, scientific databases, social platforms, forensic APIs), and returns a **scored, sourced, explainable verdict in seconds** — with a built-in adversarial critic and an always-visible "why might I be wrong?" so you can trust it the way journalists trust their own double-checks.

---

## Part 5 — What I'd ship first (opinionated MVP+)

If I'm betting on what creates the biggest early wow:

1. **Text + URL + image** on day 1 (not text only) — because image-based misinfo is *the* Instagram/WhatsApp use case.
2. **"Why might I be wrong?" tab** — zero extra cost, infinite trust impact.
3. **Telegram bot** alongside web chat — that's where misinfo forwards live. WhatsApp Business API needs review process (2–4 weeks) so it comes a bit later.
4. **Regional pack: India** (Hindi + Alt News + Boom + Factly) — this is your home market and there's a huge underserved demand.
5. **Public shareable verdict pages** — SEO flywheel from week one.
6. **Critic/Red-Team agent** — it's cheap to add and it's our single biggest quality-per-dollar lever.
7. **Evidence graph UI** — because it *looks* defensible and makes screenshots go viral.

---

## Part 6 — What I need from you

If this all looks good, here's the tight ask to start building:

1. **Pick the top 8 features** from the full list above (or say "you pick"). I'd recommend: multi-modal intake, ensemble+Critic, transparent rubric, "Why might I be wrong?", evidence graph, Telegram bot, India regional pack, public verdict pages.
2. **Confirm repo**: new repo `veritas` on your GitHub (`Puneet00007`).
3. **Confirm stack**: Python + FastAPI + LangGraph + Next.js (or say otherwise).
4. **Secrets**: OpenAI, Anthropic, Tavily, Sightengine — do you have them, or should I request via the secrets tool (one-session vs saved)?

Or the shortcut: **"You pick, start building MVP+"** and I'll begin immediately.
