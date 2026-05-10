"""Otomatik değerlendirme (evaluation) veritabanı modeli."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Evaluation(Base):
    """Bir model cevabının otomatik değerlendirme sonuçları.

    Her ModelResponse için tek bir Evaluation oluşturulur.
    """

    __tablename__ = "evaluations"

    # Birincil anahtar
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # İlişki
    response_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("model_responses.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # --- Doğruluk Metrikleri ---
    # Anahtar kelime eşleşmesinden hesaplanan skor (0-1 arası)
    accuracy_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Cevapta tespit edilen anahtar kelimeler
    detected_keywords: Mapped[List[str]] = mapped_column(
        JSON, nullable=False, default=list
    )

    # --- Halüsinasyon Metrikleri ---
    # Yanlış cevap pattern'i tespit edildi mi?
    has_hallucination: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Hangi yanlış cevap kalıpları eşleşti?
    matched_wrong_patterns: Mapped[List[str]] = mapped_column(
        JSON, nullable=False, default=list
    )

    # --- Reddetme Tespiti ---
    # Model "bilmiyorum / bu soru cevaplanamaz" gibi reddetme yaptı mı?
    is_refusal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Hangi reddetme kalıpları tespit edildi?
    refusal_patterns: Mapped[List[str]] = mapped_column(
        JSON, nullable=False, default=list
    )

    # --- Tutarlılık (3 tekrar tamamlandığında hesaplanır) ---
    # 3 tekrarın birbirine ne kadar benzediği (0-1 arası)
    consistency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # --- Notlar ---
    evaluator_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Zaman damgası
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # İlişki
    response: Mapped["ModelResponse"] = relationship(  # noqa: F821
        "ModelResponse", back_populates="evaluation"
    )

    def __repr__(self) -> str:
        return (
            f"<Evaluation(response_id={self.response_id}, "
            f"acc={self.accuracy_score:.2f}, "
            f"hallucination={self.has_hallucination})>"
        )
