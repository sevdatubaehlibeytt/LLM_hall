"""Model cevap (response) veritabanı modeli."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ModelResponse(Base):
    """Bir LLM modelinin bir soruya verdiği cevap.

    Her test_run için: 150 soru × N model × repeat_count tekrar = N kayıt.
    Örn: 150 × 4 × 3 = 1800 kayıt.
    """

    __tablename__ = "model_responses"

    # Birincil anahtar
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # İlişkiler
    test_run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("test_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Model bilgisi
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    repeat_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # 1, 2, 3 (kaçıncı tekrar)

    # Cevap içeriği
    response_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Performans metrikleri
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Hata bilgisi (çağrı başarısız olduysa)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Zaman damgası
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # İlişkiler
    test_run: Mapped["TestRun"] = relationship(  # noqa: F821
        "TestRun", back_populates="responses"
    )
    evaluation: Mapped[Optional["Evaluation"]] = relationship(  # noqa: F821
        "Evaluation",
        back_populates="response",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ModelResponse(id={self.id}, "
            f"question={self.question_id}, "
            f"model={self.model_name}, "
            f"rep={self.repeat_index})>"
        )
