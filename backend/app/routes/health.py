"""Sağlık kontrolü (health check) endpoint'leri."""

import logging
from typing import Dict, List

import httpx
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.question import Question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["Sağlık Kontrolü"])


@router.get("")
def health_check() -> dict:
    """Backend ayakta mı kontrol et."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/ollama")
async def ollama_health() -> dict:
    """Ollama servisinin erişilebilir olup olmadığını kontrol et."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()
            data = response.json()

            installed_models = [m["name"] for m in data.get("models", [])]

            return {
                "status": "ok",
                "ollama_url": settings.ollama_base_url,
                "installed_models": installed_models,
                "model_count": len(installed_models),
            }
    except httpx.ConnectError:
        return {
            "status": "error",
            "ollama_url": settings.ollama_base_url,
            "error": "Ollama servisine bağlanılamadı",
            "cozum_onerisi": (
                "Ollama servisinin çalıştığından emin olun. "
                "Komut: 'ollama serve' veya 'sudo systemctl status ollama'"
            ),
        }
    except Exception as e:
        return {
            "status": "error",
            "ollama_url": settings.ollama_base_url,
            "error": str(e),
        }


@router.get("/models")
async def models_health() -> dict:
    """Gerekli modellerin Ollama'da indirilip indirilmediğini kontrol et."""
    required_models = settings.get_default_models_list()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            installed = {m["name"] for m in data.get("models", [])}
    except Exception as e:
        return {
            "status": "error",
            "error": f"Ollama'ya erişilemiyor: {e}",
        }

    available: List[str] = []
    missing: List[str] = []

    for model in required_models:
        if model in installed:
            available.append(model)
        else:
            missing.append(model)

    return {
        "status": "ok" if not missing else "warning",
        "available": available,
        "missing": missing,
        "required": required_models,
        "cozum_onerisi": (
            None
            if not missing
            else f"Eksik modelleri indirmek için: {', '.join(f'ollama pull {m}' for m in missing)}"
        ),
    }


@router.get("/database")
def database_health(db: Session = Depends(get_db)) -> dict:
    """Veritabanı durumunu kontrol et."""
    try:
        question_count = db.query(Question).count()
        return {
            "status": "ok",
            "database_url": settings.database_url.split("://")[0] + "://...",
            "question_count": question_count,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }
