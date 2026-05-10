#!/bin/bash
# ============================================
# LLM Halüsinasyon Tespit Backend
# Sunucu Başlatma Scripti
# ============================================
# Bu script FastAPI sunucusunu uvicorn ile başlatır.
#
# Kullanım: ./scripts/start.sh

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Proje kök dizinine git
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$PROJECT_DIR"

# venv kontrolü
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ venv klasörü bulunamadı!${NC}"
    echo "   Önce kurulumu çalıştırın: ./scripts/setup.sh"
    exit 1
fi

# .env kontrolü
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env dosyası bulunamadı!${NC}"
    echo "   Önce kurulumu çalıştırın: ./scripts/setup.sh"
    exit 1
fi

# Sanal ortamı aktive et
source venv/bin/activate

# .env'den port ve host oku (varsayılanlar ile)
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

# .env dosyasından okuma (varsa)
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep -E '^(HOST|PORT|DEBUG)=' | xargs)
fi

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}🚀 Backend Başlatılıyor${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "Adres: ${GREEN}http://${HOST}:${PORT}${NC}"
echo -e "Swagger UI: ${GREEN}http://localhost:${PORT}/docs${NC}"
echo -e "Sağlık kontrolü: ${GREEN}http://localhost:${PORT}/api/health${NC}"
echo ""
echo -e "${YELLOW}Durdurmak için Ctrl+C'ye basın.${NC}"
echo ""

# Uvicorn başlat
# --reload: Geliştirme modunda dosya değişikliklerini izle
uvicorn app.main:app \
    --host "$HOST" \
    --port "$PORT" \
    --reload \
    --log-level info
