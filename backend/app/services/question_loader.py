"""JSON dosyasından sorul yükleyen servis.

Reproducibility için dosyanın SHA-256 hash'i hesaplanır ve loglanır.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Tuple

from sqlalchemy.orm import Session

from app.models.question import Question

logger = logging.getLogger(__name__)


def calculate_file_hash(file_path: Path) -> str:
    """Dosyanın SHA-256 hash'ini hesapla.

    TR-Dizin için reproducibility (tekrar üretilebilirlik) gereksinimi.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_questions_from_json(
    db: Session,
    json_path: Path,
    skip_existing: bool = True,
) -> Tuple[int, int, str]:
    """JSON dosyasından soruları okuyup veritabanına kaydet.

    Args:
        db: SQLAlchemy session
        json_path: JSON dosyasının yolu
        skip_existing: Mevcut soruları atla (True) veya güncelle (False)

    Returns:
        (yuklenen_sayisi, atlanan_sayisi, dosya_hashi)

    Raises:
        FileNotFoundError: JSON dosyası bulunamazsa
        json.JSONDecodeError: JSON formatı bozuksa
        KeyError: Beklenen alanlar eksikse
    """
    if not json_path.exists():
        raise FileNotFoundError(
            f"Soru seti dosyası bulunamadı: {json_path}\n"
            f"Lütfen JSON dosyasını şu konuma kopyalayın: {json_path}"
        )

    # Dosya hash'i (reproducibility için)
    file_hash = calculate_file_hash(json_path)
    logger.info(f"Soru seti dosyası hash: {file_hash}")

    # JSON'ı oku
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Format doğrulama
    if "sorular" not in data:
        raise KeyError(
            "JSON dosyasında 'sorular' anahtarı bulunamadı. "
            "Dosya formatı doğru mu kontrol edin."
        )

    questions_data = data["sorular"]
    if not isinstance(questions_data, list):
        raise ValueError("'sorular' bir liste olmalı")

    total_loaded = 0
    total_skipped = 0

    for q_data in questions_data:
        try:
            question_id = q_data["id"]

            # Mevcut kayıt kontrolü
            existing = db.query(Question).filter(Question.id == question_id).first()

            if existing and skip_existing:
                total_skipped += 1
                continue

            if existing and not skip_existing:
                # Mevcut soruyu güncelle
                existing.kategori = q_data.get("kategori", "")
                existing.alt_kategori = q_data.get("alt_kategori", "")
                existing.zorluk = q_data.get("zorluk", "")
                existing.soru_tipi = q_data.get("soru_tipi", "")
                existing.soru = q_data.get("soru", "")
                existing.beklenen_cevap = q_data.get("beklenen_cevap", "")
                existing.halusinasyon_tuzagi = q_data.get("halusinasyon_tuzagi")
                existing.degerlendirme_anahtar_kelimeler = q_data.get(
                    "degerlendirme_anahtar_kelimeler", []
                )
                existing.yanlis_cevap_ornekleri = q_data.get(
                    "yanlis_cevap_ornekleri", []
                )
                existing.kaynak = q_data.get("kaynak")
                total_loaded += 1
            else:
                # Yeni soru
                question = Question(
                    id=question_id,
                    kategori=q_data.get("kategori", ""),
                    alt_kategori=q_data.get("alt_kategori", ""),
                    zorluk=q_data.get("zorluk", ""),
                    soru_tipi=q_data.get("soru_tipi", ""),
                    soru=q_data.get("soru", ""),
                    beklenen_cevap=q_data.get("beklenen_cevap", ""),
                    halusinasyon_tuzagi=q_data.get("halusinasyon_tuzagi"),
                    degerlendirme_anahtar_kelimeler=q_data.get(
                        "degerlendirme_anahtar_kelimeler", []
                    ),
                    yanlis_cevap_ornekleri=q_data.get("yanlis_cevap_ornekleri", []),
                    kaynak=q_data.get("kaynak"),
                )
                db.add(question)
                total_loaded += 1

        except KeyError as e:
            logger.error(f"Soru atlandı, eksik alan: {e}, soru: {q_data.get('id', '?')}")
            continue

    db.commit()

    logger.info(
        f"Soru yükleme tamamlandı: {total_loaded} yüklendi, "
        f"{total_skipped} atlandı"
    )

    return total_loaded, total_skipped, file_hash


def get_question_count(db: Session) -> int:
    """Veritabanındaki toplam soru sayısını döndür."""
    return db.query(Question).count()
