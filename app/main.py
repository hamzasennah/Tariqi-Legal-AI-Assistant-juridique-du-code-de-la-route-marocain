from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import sys
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tariqi import AppConfig, FineCalculator, TariqiAssistant, build_index
from tariqi.procedures import ProcedureGuide
from tariqi.source_registry import SourceRegistry


app = FastAPI(
    title="Tariqi Legal AI",
    version="2.0.0",
    description="Assistant juridique RAG du code de la route marocain.",
)
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=800)
    top_k: int = Field(default=5, ge=3, le=8)


class CalculateRequest(BaseModel):
    infraction: str = Field(min_length=2, max_length=300)
    delay: str = Field(default="24h", pattern="^(24h|15j|30j)$")


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    return AppConfig.from_env()


@lru_cache(maxsize=1)
def get_assistant() -> TariqiAssistant:
    config = get_config()
    if not config.index_path.exists():
        build_index(config)
    return TariqiAssistant(config)


@lru_cache(maxsize=1)
def get_calculator() -> FineCalculator:
    return FineCalculator(get_config().infractions_csv)


@lru_cache(maxsize=1)
def get_procedure_guide() -> ProcedureGuide:
    return ProcedureGuide(get_config().procedures_path)


def source_payload(item: Any) -> dict[str, Any]:
    metadata = item.chunk.metadata
    return {
        "score": round(item.score, 3),
        "source_id": item.chunk.source_id,
        "authority": metadata.get("authority", ""),
        "title": metadata.get("title", ""),
        "document": metadata.get("document", ""),
        "section": metadata.get("article_or_section", ""),
        "date": metadata.get("date_source", ""),
        "trust_level": metadata.get("trust_level", ""),
        "url": metadata.get("url", ""),
        "excerpt": item.chunk.text,
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "app_name": "Tariqi Legal AI",
        },
    )


@app.get("/health")
def health() -> dict[str, str]:
    config = get_config()
    return {
        "status": "ok",
        "index": "ready" if config.index_path.exists() else "missing",
    }


@app.post("/api/ask")
def ask(payload: AskRequest) -> dict[str, Any]:
    try:
        answer = get_assistant().ask(payload.question.strip(), top_k=payload.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "question": answer.question,
        "answer_markdown": answer.to_markdown(),
        "confidence": answer.confidence,
        "sources": [source_payload(item) for item in answer.sources],
    }


@app.post("/api/calculate")
def calculate(payload: CalculateRequest) -> dict[str, Any]:
    result = get_calculator().calculate(payload.infraction, delay=payload.delay)
    return {
        "matched": result.matched,
        "message": result.message,
        "delay": result.delay,
        "amount": result.amount,
        "points": result.points,
        "infraction": result.infraction,
    }


@app.get("/api/infractions")
def infractions(q: str = "", limit: int = 8) -> dict[str, Any]:
    calculator = get_calculator()
    rows = calculator.search(q, limit=limit) if q.strip() else calculator.rows[:limit]
    return {"items": rows}


@app.get("/api/procedure")
def procedure(q: str) -> dict[str, Any]:
    matched = get_procedure_guide().match(q)
    return {"procedure": matched}


@app.get("/api/procedures")
def procedures() -> dict[str, Any]:
    return {"items": get_procedure_guide().all()}


@app.get("/api/sources")
def sources() -> dict[str, Any]:
    registry = SourceRegistry.from_json(get_config().source_manifest_path)
    return {"items": registry.sources}
