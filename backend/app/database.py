"""Veritabanı bağlantısı ve session yönetimi."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Tüm SQLAlchemy modellerinin temel sınıfı."""

    pass


# Engine oluşturma
# SQLite için özel argümanlar (multi-thread desteği)
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,  # Debug modunda SQL sorgularını yazdır
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency injection için DB session sağlayıcı.

    Kullanım:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager olarak DB session kullanımı.

    Pipeline runner gibi async/background işlerde kullanılır.

    Kullanım:
        with get_db_context() as db:
            db.add(item)
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database() -> None:
    """Veritabanı tablolarını oluştur (yoksa).

    Tüm modellerin Base.metadata'ya kayıtlı olduğundan emin ol.
    """
    # Modelleri import et ki Base.metadata'ya kaydedilsinler
    from app.models import (  # noqa: F401
        evaluation,
        manual_label,
        model_response,
        question,
        test_run,
    )

    Base.metadata.create_all(bind=engine)
