"""Soru (Question) Pydantic şemaları."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QuestionResponse(BaseModel):
    """API'de döndürülen soru formatı."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Soru ID (örn: MAT-001)")
    kategori: str = Field(..., description="Ana kategori")
    alt_kategori: str = Field(..., description="Alt kategori")
    zorluk: str = Field(..., description="Zorluk seviyesi: kolay/orta/zor")
    soru_tipi: str = Field(..., description="Soru tipi: hesaplama/tuzak/manipulasyon vb.")

    soru: str = Field(..., description="Modele gönderilecek soru metni")
    beklenen_cevap: str = Field(..., description="Beklenen doğru cevap")
    halusinasyon_tuzagi: Optional[str] = Field(
        None, description="Halüsinasyona yol açabilecek tuzak"
    )

    degerlendirme_anahtar_kelimeler: List[str] = Field(
        default_factory=list,
        description="Cevapta aranacak anahtar kelimeler (doğru cevap için)",
    )
    yanlis_cevap_ornekleri: List[str] = Field(
        default_factory=list,
        description="Halüsinasyon tespiti için yanlış cevap kalıpları",
    )

    kaynak: Optional[str] = Field(None, description="Kaynak bilgisi")

    created_at: datetime


class QuestionFilter(BaseModel):
    """Soru filtreleme parametreleri."""

    kategori: Optional[str] = Field(None, description="Kategoriye göre filtrele")
    zorluk: Optional[str] = Field(None, description="Zorluğa göre filtrele")
    soru_tipi: Optional[str] = Field(None, description="Soru tipine göre filtrele")
    limit: int = Field(150, ge=1, le=500, description="Maksimum sonuç sayısı")
    offset: int = Field(0, ge=0, description="Atlanacak sonuç sayısı")


class QuestionsLoadResult(BaseModel):
    """JSON'dan soru yükleme işlemi sonucu."""

    success: bool
    total_loaded: int = Field(..., description="Yüklenen soru sayısı")
    total_skipped: int = Field(0, description="Atlanan (zaten var olan) soru sayısı")
    file_path: str
    file_hash: Optional[str] = Field(None, description="Dosyanın SHA-256 hash'i")
    message: str
