#!/bin/bash
# ============================================
# LLM Halüsinasyon Tespit Backend
# İlk Kurulum Scripti
# ============================================
# Bu script şunları yapar:
#   1. Python sanal ortam (venv) oluşturur
#   2. Bağımlılıkları yükler
#   3. .env dosyasını .env.example'dan kopyalar
#   4. logs/ klasörünü oluşturur
#
# Kullanım: ./scripts/setup.sh

set -e  # Herhangi bir hata olursa scripti durdur

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Proje kök dizinine git (script'in çalıştırıldığı yerden bağımsız olarak)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$PROJECT_DIR"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}🔧 LLM Halüsinasyon Backend - Kurulum${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# 1. Python kontrolü
echo -e "${YELLOW}[1/5]${NC} Python sürümü kontrol ediliyor..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 bulunamadı!${NC}"
    echo "   Çözüm: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✅ Python $PYTHON_VERSION bulundu${NC}"

# Python 3.10+ kontrolü
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}❌ Python 3.10 veya üzeri gerekli (mevcut: $PYTHON_VERSION)${NC}"
    exit 1
fi

# 2. Sanal ortam oluştur
echo ""
echo -e "${YELLOW}[2/5]${NC} Python sanal ortamı oluşturuluyor..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  venv klasörü zaten var, atlanıyor${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✅ venv klasörü oluşturuldu${NC}"
fi

# 3. Sanal ortamı aktive et ve paketleri yükle
echo ""
echo -e "${YELLOW}[3/5]${NC} Bağımlılıklar yükleniyor (birkaç dakika sürebilir)..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ Tüm paketler yüklendi${NC}"

# 4. .env dosyası
echo ""
echo -e "${YELLOW}[4/5]${NC} Ortam değişkenleri yapılandırılıyor..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env dosyası oluşturuldu (.env.example'dan kopyalandı)${NC}"
else
    echo -e "${YELLOW}⚠️  .env dosyası zaten var, atlanıyor${NC}"
fi

# 5. Klasörleri hazırla
echo ""
echo -e "${YELLOW}[5/5]${NC} Çalışma klasörleri hazırlanıyor..."
mkdir -p logs data
echo -e "${GREEN}✅ logs/ ve data/ klasörleri hazır${NC}"

# Veri seti kontrolü
echo ""
DATA_FILE="data/halusinasyon_test_sorulari.json"
if [ ! -f "$DATA_FILE" ]; then
    echo -e "${YELLOW}⚠️  Soru seti dosyası bulunamadı: $DATA_FILE${NC}"
    echo "   Lütfen 'halusinasyon_test_sorulari.json' dosyasını $DATA_FILE konumuna kopyalayın."
else
    echo -e "${GREEN}✅ Soru seti dosyası bulundu: $DATA_FILE${NC}"
fi

# Tamamlandı
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✨ Kurulum tamamlandı!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Backend'i başlatmak için:"
echo -e "  ${BLUE}./scripts/start.sh${NC}"
echo ""
echo -e "Sağlık kontrolü için:"
echo -e "  ${BLUE}curl http://localhost:8000/api/health${NC}"
echo ""
