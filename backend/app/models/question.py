"""Soru veritabanı modeli."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Question(Base):
    """LLM halüsinasyon test sorusu.

    JSON soru setinden yüklenir ve modellere gönderilen prompt'ları içerir.
    """

    __tablename__ = "questions"

    # Birincil anahtar - JSON'daki ID korunur (örn: "MAT-001")
    id: Mapped[str] = mapped_column(String(20), primary_key=True)

    # Sınıflandırma
    kategori: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    alt_kategori: Mapped[str] = mapped_column(String(100), nullable=False)
    zorluk: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    soru_tipi: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    # Soru içeriği
    soru: Mapped[str] = mapped_column(Text, nullable=False)
    beklenen_cevap: Mapped[str] = mapped_column(Text, nullable=False)
    halusinasyon_tuzagi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Değerlendirme verileri (JSON liste olarak saklanır)
    degerlendirme_anahtar_kelimeler: Mapped[List[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    yanlis_cevap_ornekleri: Mapped[List[str]] = mapped_column(
        JSON, nullable=False, default=list
    )

    # Kaynak
    kaynak: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Zaman damgaları
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, kategori={self.kategori})>"
