"""Soru (Question) API endpoint'leri."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.question import Question
from app.schemas.question import QuestionResponse, QuestionsLoadResult
from app.services.question_loader import (
    get_question_count,
    load_questions_from_json,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/questions", tags=["Sorular"])


@router.get("", response_model=List[QuestionResponse])
def list_questions(
    kategori: Optional[str] = Query(None, description="Kategoriye göre filtrele"),
    zorluk: Optional[str] = Query(None, description="Zorluğa göre filtrele"),
    soru_tipi: Optional[str] = Query(None, description="Soru tipine göre filtrele"),
    limit: int = Query(150, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> List[Question]:
    """Soruları listele.

    Filtre parametreleri ile sınırlandırılabilir.
    """
    query = db.query(Question)

    if kategori:
        query = query.filter(Question.kategori == kategori)
    if zorluk:
        query = query.filter(Question.zorluk == zorluk)
    if soru_tipi:
        query = query.filter(Question.soru_tipi == soru_tipi)

    questions = query.offset(offset).limit(limit).all()
    return questions


@router.get("/stats")
def get_questions_stats(db: Session = Depends(get_db)) -> dict:
    """Soru istatistiklerini döndür.

    Toplam soru sayısı + kategori/zorluk/tip dağılımları.
    """
    total = get_question_count(db)

    kategori_dist = dict(
        db.query(Question.kategori, func.count(Question.id))
        .group_by(Question.kategori)
        .all()
    )
    zorluk_dist = dict(
        db.query(Question.zorluk, func.count(Question.id))
        .group_by(Question.zorluk)
        .all()
    )
    tip_dist = dict(
        db.query(Question.soru_tipi, func.count(Question.id))
        .group_by(Question.soru_tipi)
        .all()
    )

    return {
        "total": total,
        "kategori_dagilimi": kategori_dist,
        "zorluk_dagilimi": zorluk_dist,
        "soru_tipi_dagilimi": tip_dist,
    }


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: str, db: Session = Depends(get_db)) -> Question:
    """ID ile tek bir soruyu getir."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Soru bulunamadı: {question_id}",
        )
    return question


@router.post(
    "/load-from-json",
    response_model=QuestionsLoadResult,
    status_code=status.HTTP_201_CREATED,
)
def load_questions(
    skip_existing: bool = Query(
        True, description="Mevcut soruları atla (False: güncelle)"
    ),
    db: Session = Depends(get_db),
) -> QuestionsLoadResult:
    """JSON dosyasından soruları veritabanına yükle.

    Kaynak dosya: settings.questions_json_path
    Varsayılan: ./data/halusinasyon_test_sorulari.json
    """
    json_path = settings.get_questions_json_absolute_path()

    try:
        loaded, skipped, file_hash = load_questions_from_json(
            db=db,
            json_path=json_path,
            skip_existing=skip_existing,
        )
        return QuestionsLoadResult(
            success=True,
            total_loaded=loaded,
            total_skipped=skipped,
            file_path=str(json_path),
            file_hash=file_hash,
            message=f"{loaded} soru yüklendi, {skipped} soru atlandı.",
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"JSON formatı hatalı: {e}",
        )
    except Exception as e:
        logger.exception("Soru yükleme sırasında beklenmedik hata")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Soru yükleme hatası: {e}",
        )
