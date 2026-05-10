"""FastAPI uygulamasının giriş noktası.

Bu dosya FastAPI uygulamasını oluşturur, route'ları kaydeder,
CORS ayarlarını yapar ve startup/shutdown event'lerini yönetir.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_database
from app.routes import health, questions

# --- Loglama Yapılandırması ---
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü yöneticisi.

    Startup: Veritabanı tablolarını oluştur, sağlık kontrolleri yap.
    Shutdown: Kaynakları temizle.
    """
    # === STARTUP ===
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} başlatılıyor...")
    logger.info("=" * 60)

    # Veritabanı tablolarını oluştur
    logger.info("📦 Veritabanı tabloları kontrol ediliyor...")
    init_database()
    logger.info("✅ Veritabanı hazır")

    # JSON dosyası kontrolü (uyarı amaçlı)
    json_path = settings.get_questions_json_absolute_path()
    if not json_path.exists():
        logger.warning(
            f"⚠️  Soru seti dosyası bulunamadı: {json_path}\n"
            f"   Lütfen JSON dosyasını şu konuma kopyalayın."
        )
    else:
        logger.info(f"✅ Soru seti dosyası bulundu: {json_path}")

    logger.info(f"🌐 Sunucu http://{settings.host}:{settings.port} adresinde dinliyor")
    logger.info(f"📚 API dokümantasyonu: http://{settings.host}:{settings.port}/docs")
    logger.info("=" * 60)

    yield

    # === SHUTDOWN ===
    logger.info("👋 Uygulama kapatılıyor...")


# --- FastAPI Uygulaması ---
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Türkçe LLM Halüsinasyon Tespit Projesi Backend API'si.\n\n"
        "Bu API, yerel Ollama modellerinde (Mistral, Llama 3.1, Qwen 2.5 vb.) "
        "150 soruluk test setini koşturmak ve sonuçları değerlendirmek için "
        "kullanılır."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Route'ları Kaydet ---
app.include_router(health.router)
app.include_router(questions.router)


# --- Kök Endpoint ---
@app.get("/", tags=["Root"])
def root() -> dict:
    """Kök endpoint - API'nin ayakta olduğunu gösterir."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health",
    }
