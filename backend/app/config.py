"""Uygulama ayarları - .env dosyasından yüklenir."""

from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Tüm uygulama ayarları .env dosyasından okunur."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Uygulama ---
    app_name: str = "LLM Halusinasyon Tespit Backend"
    app_version: str = "0.1.0"
    debug: bool = True
    log_level: str = "INFO"

    # --- Sunucu ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- Veritabanı ---
    database_url: str = "sqlite:///./llm_halusinasyon.db"

    # --- Ollama ---
    ollama_base_url: str = "http://localhost:11434"
    ollama_request_timeout: int = 180

    # --- Pipeline Varsayılanları ---
    default_temperature: float = 0.0
    default_seed: int = 42
    default_top_p: float = 0.9
    default_max_tokens: int = 512
    default_repeat_count: int = 3

    # Hata yönetimi
    max_retry_count: int = 2
    retry_backoff_seconds: int = 5

    # --- Veri Dosyası ---
    questions_json_path: str = "./data/halusinasyon_test_sorulari.json"

    # --- CORS ---
    cors_origins: str = "*"

    # --- Modeller ---
    default_models: str = (
        "mistral:7b,llama3.1:8b,qwen2.5:7b,"
        "ytagalar/trendyol-llm-7b-chat-dpo-v1.0-gguf"
    )

    @field_validator("cors_origins")
    @classmethod
    def parse_cors(cls, v: str) -> str:
        """CORS ayarlarını doğrula."""
        return v.strip()

    def get_cors_origins_list(self) -> List[str]:
        """CORS origin'lerini liste olarak döndür."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def get_default_models_list(self) -> List[str]:
        """Varsayılan modelleri liste olarak döndür."""
        return [m.strip() for m in self.default_models.split(",") if m.strip()]

    def get_questions_json_absolute_path(self) -> Path:
        """JSON dosyasının mutlak yolunu döndür."""
        path = Path(self.questions_json_path)
        if not path.is_absolute():
            # Proje kök dizinine göre çöz
            base_dir = Path(__file__).resolve().parent.parent
            path = base_dir / path
        return path.resolve()


# Singleton settings nesnesi
settings = Settings()
