"""Manuel etiketleme (manual label) veritabanı modeli.

Cohen's Kappa hesaplaması için iki farklı değerlendiricinin
aynı cevabı bağımsız olarak etiketlemesi gerekir.
"""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


from app.database import Base


class LabelValue(str, enum.Enum):
    """Manuel etiket değerleri."""

    CORRECT = "correct"  # Tamamen doğru
    INCORRECT = "incorrect"  # Yanlış / halüsinasyon var
    PARTIAL = "partial"  # Kısmen doğru
    REFUSAL = "refusal"  # Cevap verme reddi (tuzaklarda doğru olabilir)
    UNCLEAR = "unclear"  # Belirsiz / değerlendirilemez


class ManualLabel(Base):
    """Manuel olarak verilen etiket.

    Bir ModelResponse birden fazla manuel etiket alabilir
    (farklı değerlendiricilerden), Cohen's Kappa hesabı için.
    """

    __tablename__ = "manual_labels"

    # Birincil anahtar
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # İlişki
    response_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("model_responses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Değerlendirici kimliği (örn: "evaluator_1", "tuba", "atakan")
    evaluator_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Etiket
    label: Mapped[LabelValue] = mapped_column(Enum(LabelValue), nullable=False)

    # Notlar
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Zaman damgası
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<ManualLabel(response_id={self.response_id}, "
            f"evaluator={self.evaluator_id}, label={self.label})>"
        )
