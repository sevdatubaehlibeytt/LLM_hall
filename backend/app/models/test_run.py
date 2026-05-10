"""Test çalıştırma (test run) veritabanı modeli."""

import enum
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import JSON, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TestRunStatus(str, enum.Enum):
    """Test çalıştırma durumları."""

    PENDING = "pending"  # Beklemede
    RUNNING = "running"  # Devam ediyor
    COMPLETED = "completed"  # Tamamlandı
    FAILED = "failed"  # Başarısız
    CANCELLED = "cancelled"  # İptal edildi
    PAUSED = "paused"  # Duraklatıldı


class TestRun(Base):
    """LLM modellerin değerlendirildiği bir test oturumu.

    TR-Dizin için reproducibility (tekrar üretilebilirlik) sağlamak amacıyla
    kullanılan tüm parametreler ve model versiyonları kaydedilir.
    """

    __tablename__ = "test_runs"

    # Birincil anahtar - UUID
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Tanım
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Durum
    status: Mapped[TestRunStatus] = mapped_column(
        Enum(TestRunStatus),
        nullable=False,
        default=TestRunStatus.PENDING,
        index=True,
    )

    # Test parametreleri
    model_list: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    repeat_count: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    seed: Mapped[int] = mapped_column(Integer, nullable=False, default=42)
    top_p: Mapped[float] = mapped_column(Float, nullable=False, default=0.9)
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=512)

    # İlerleme
    total_calls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_calls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_calls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Reproducibility için (TR-Dizin gereksinimi)
    ollama_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    question_set_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    model_digests: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Format: {"mistral:7b": "sha256:abc...", "llama3.1:8b": "sha256:def..."}

    # Zaman damgaları (UTC)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Hata bilgisi
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # İlişkiler
    responses: Mapped[List["ModelResponse"]] = relationship(  # noqa: F821
        "ModelResponse",
        back_populates="test_run",
        cascade="all, delete-orphan",
    )

    @property
    def progress_percentage(self) -> float:
        """İlerleme yüzdesini hesapla."""
        if self.total_calls == 0:
            return 0.0
        return (self.completed_calls / self.total_calls) * 100

    def __repr__(self) -> str:
        return f"<TestRun(id={self.id[:8]}, name={self.name}, status={self.status})>"
