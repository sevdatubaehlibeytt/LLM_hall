#!/bin/bash
# ============================================
# Sistem Hazırlık Kontrol Scripti
# ============================================
# Bu script kurulum öncesi sistemde her şeyin
# hazır olup olmadığını kontrol eder.

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}🔍 Sistem Hazırlık Kontrolü${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

ALL_OK=true

# Python kontrolü
echo -n "Python 3.10+: "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Bulunamadı${NC}"
    ALL_OK=false
fi

# pip kontrolü
echo -n "pip: "
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅ $PIP_VERSION${NC}"
else
    echo -e "${RED}❌ Bulunamadı${NC}"
    ALL_OK=false
fi

# venv modülü
echo -n "python3-venv: "
if python3 -c "import venv" 2>/dev/null; then
    echo -e "${GREEN}✅ Mevcut${NC}"
else
    echo -e "${RED}❌ Bulunamadı (sudo apt install python3-venv)${NC}"
    ALL_OK=false
fi

# Ollama kontrolü
echo -n "Ollama: "
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>&1)
    echo -e "${GREEN}✅ $OLLAMA_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Bulunamadı${NC}"
    echo "      Kurulum: curl -fsSL https://ollama.com/install.sh | sh"
fi

# Ollama servis kontrolü
echo -n "Ollama servisi: "
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Çalışıyor${NC}"

    # Yüklü modeller
    INSTALLED_MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; data = json.load(sys.stdin); print(', '.join(m['name'] for m in data.get('models', [])))")
    if [ -n "$INSTALLED_MODELS" ]; then
        echo -e "      Yüklü modeller: ${GREEN}$INSTALLED_MODELS${NC}"
    else
        echo -e "      ${YELLOW}⚠️  Henüz hiç model indirilmemiş${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Çalışmıyor${NC}"
    echo "      Başlatmak için: ollama serve"
fi

# GPU kontrolü
echo -n "NVIDIA GPU: "
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader 2>/dev/null | head -1)
    echo -e "${GREEN}✅ $GPU_NAME ($GPU_MEMORY)${NC}"
else
    echo -e "${YELLOW}⚠️  nvidia-smi bulunamadı${NC}"
    echo "      GPU kullanılamayabilir, modeller CPU'da yavaş çalışır."
fi

# JSON soru seti kontrolü
echo -n "Soru seti dosyası: "
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"
DATA_FILE="$PROJECT_DIR/data/halusinasyon_test_sorulari.json"

if [ -f "$DATA_FILE" ]; then
    QUESTION_COUNT=$(python3 -c "import json; data = json.load(open('$DATA_FILE')); print(len(data.get('sorular', [])))" 2>/dev/null)
    echo -e "${GREEN}✅ Bulundu ($QUESTION_COUNT soru)${NC}"
else
    echo -e "${YELLOW}⚠️  Bulunamadı${NC}"
    echo "      Konum: $DATA_FILE"
fi

# Disk alanı
echo -n "Disk alanı: "
AVAILABLE_GB=$(df -BG "$PROJECT_DIR" | awk 'NR==2 {print $4}' | tr -d 'G')
if [ "$AVAILABLE_GB" -gt 20 ]; then
    echo -e "${GREEN}✅ ${AVAILABLE_GB}GB boş${NC}"
else
    echo -e "${YELLOW}⚠️  Sadece ${AVAILABLE_GB}GB boş (modeller için 20GB+ önerilir)${NC}"
fi

echo ""
echo -e "${BLUE}============================================${NC}"
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✨ Sistem hazır!${NC}"
    echo -e "Şimdi kurulumu başlatın: ${BLUE}./scripts/setup.sh${NC}"
else
    echo -e "${RED}❌ Bazı bağımlılıklar eksik. Yukarıdaki uyarıları takip edin.${NC}"
fi
echo -e "${BLUE}============================================${NC}"
