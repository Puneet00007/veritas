"""Media Forensics Agent (stub).

Planned pipeline (image):
  1. Reverse image search: Google Lens (SerpAPI) + Bing Visual + TinEye.
  2. pHash / aHash: cluster near-duplicates and find earliest appearance.
  3. AI-generation detection: Sightengine + Hive.
  4. Deepfake detection: Sightengine deepfake model.
  5. EXIF + C2PA content-credentials read.

Audio pipeline:
  1. Whisper transcription.
  2. AudD / ACRCloud music fingerprint.
  3. Voice-cloning detection (Pindrop / Resemble Detect).

Video pipeline:
  1. yt-dlp → keyframes + audio track.
  2. Image pipeline on frames; audio pipeline on track.
  3. Lip-sync inconsistency check.

Spec reference: user brief — multi-modal requirement.
"""


async def analyze_image(path: str) -> dict:
    raise NotImplementedError("Media forensics — scheduled for PR #2")


async def analyze_audio(path: str) -> dict:
    raise NotImplementedError("Media forensics (audio) — scheduled for PR #2")


async def analyze_video(path: str) -> dict:
    raise NotImplementedError("Media forensics (video) — scheduled for PR #2")
