from __future__ import annotations

import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from .config import settings
from .orchestrator import Orchestrator
from .schemas import CheckRequest, CheckResult

logging.basicConfig(level=settings.log_level)

app = FastAPI(title="Veritas", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()


@app.get("/healthz")
async def healthz() -> dict:
    return {
        "status": "ok",
        "llm_configured": settings.has_llm,
        "tavily_configured": bool(settings.tavily_api_key),
        "google_fact_check_configured": bool(settings.google_fact_check_api_key),
    }


@app.post("/api/check", response_model=CheckResult)
async def check(req: CheckRequest) -> CheckResult:
    return await orchestrator.run(req.input)


@app.post("/api/check/stream")
async def check_stream(req: CheckRequest):
    async def gen():
        async for name, payload in orchestrator.run_stream(req.input):
            yield {"event": name, "data": json.dumps(payload, default=str)}

    return EventSourceResponse(gen())
