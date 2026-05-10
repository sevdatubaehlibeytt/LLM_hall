# 🔬 LLM Halüsinasyon Tespit Backend

Türkçe LLM Halüsinasyon Tespit Projesi'nin backend servisidir. Yerel Ollama modelleri (Mistral, Llama 3.1, Qwen 2.5, Trendyol-LLM) üzerinde 150 soruluk Türkçe test setini koşturup sonuçları otomatik değerlendiren bir FastAPI uygulaması.

## 📋 İçindekiler

- [Sistem Gereksinimleri](#sistem-gereksinimleri)
- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Detaylı Kurulum](#detaylı-kurulum)
- [Kullanım](#kullanım)
- [API Dokümantasyonu](#api-dokümantasyonu)
- [Sorun Giderme](#sorun-giderme)
- [Proje Yapısı](#proje-yapısı)

## 🖥️ Sistem Gereksinimleri

### Donanım (Önerilen)
- **RAM:** 16 GB veya üzeri
- **GPU:** NVIDIA RTX 3050+ (6 GB VRAM, 7B modeller için)
- **Disk:** 20+ GB boş alan (modeller için)
- **CPU:** Modern 4+ çekirdek işlemci

### Yazılım
- Linux veya WSL2 (Ubuntu 22.04 önerilir)
- Python 3.10+
- Ollama 0.20+ (yerel olarak çalışır durumda)
- NVIDIA CUDA driver (GPU kullanımı için)

## ⚡ Hızlı Başlangıç

```bash
# 1. Sistemi kontrol et
./scripts/check_system.sh

# 2. Kurulum
./scripts/setup.sh

# 3. Soru setini data/ klasörüne kopyala
cp /path/to/halusinasyon_test_sorulari.json data/

# 4. Backend'i başlat
./scripts/start.sh

# 5. Tarayıcıda Swagger UI'ı aç
# http://localhost:8000/docs
```

## 🔧 Detaylı Kurulum

### 1. Sistem Hazırlığı

WSL2 (Ubuntu) içinde aşağıdaki paketleri yükleyin:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl
```

### 2. Ollama Kurulumu

Eğer henüz yüklü değilse:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Servisi başlatın:

```bash
ollama serve
```

(Veya systemd ile arka planda otomatik başlat: `sudo systemctl start ollama`)

### 3. Modelleri İndirin

Test edilecek modeller (toplam ~17 GB):

```bash
ollama pull mistral:7b
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
ollama pull ytagalar/trendyol-llm-7b-chat-dpo-v1.0-gguf
```

### 4. Repoyu Klonlayın

```bash
git clone https://github.com/Atakan/LLM_hall.git
cd LLM_hall/backend
```

### 5. Backend Kurulumu

```bash
chmod +x scripts/*.sh
./scripts/check_system.sh    # Sistem kontrolü
./scripts/setup.sh            # Bağımlılıkları yükle
```

### 6. Soru Setini Kopyalayın

`halusinasyon_test_sorulari.json` dosyasını `data/` klasörüne kopyalayın:

```bash
cp /path/to/halusinasyon_test_sorulari.json data/
```

### 7. Backend'i Başlatın

```bash
./scripts/start.sh
```

Sunucu `http://localhost:8000` adresinde çalışmaya başlar.

### 8. İlk Test

```bash
# Sağlık kontrolü
curl http://localhost:8000/api/health

# Soruları yükle (JSON'dan veritabanına)
curl -X POST http://localhost:8000/api/questions/load-from-json

# Soruları listele
curl http://localhost:8000/api/questions?limit=5
```

## 📚 API Dokümantasyonu

Sunucu çalışırken otomatik üretilen dokümantasyona erişebilirsiniz:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Ana Endpoint'ler (Aşama 1)

| Metod | Endpoint | Açıklama |
|-------|----------|----------|
| GET | `/api/health` | Backend sağlık kontrolü |
| GET | `/api/health/ollama` | Ollama bağlantı kontrolü |
| GET | `/api/health/models` | Modellerin indirilmiş olup olmadığını kontrol |
| GET | `/api/health/database` | Veritabanı durumu |
| GET | `/api/questions` | Soruları listele (filtreli) |
| GET | `/api/questions/{id}` | Tek soru getir |
| GET | `/api/questions/stats` | Soru istatistikleri |
| POST | `/api/questions/load-from-json` | JSON'dan soruları yükle |

> **Not:** Aşama 1 sadece soru yönetimini içerir. Test çalıştırma, pipeline ve raporlama endpoint'leri Aşama 2-5'te eklenecek.

## 🐛 Sorun Giderme

### "ModuleNotFoundError: No module named 'app'"

Sanal ortam aktive edilmemiş olabilir:

```bash
source venv/bin/activate
```

### "Address already in use" (port 8000 dolu)

Port'u değiştirin:

```bash
# .env dosyasında
PORT=8001
```

Veya çakışan süreci bulup kapatın:

```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### "Soru seti dosyası bulunamadı"

JSON dosyasının `data/halusinasyon_test_sorulari.json` konumunda olduğundan emin olun:

```bash
ls -la data/
```

### Ollama'ya bağlanılamıyor

```bash
# Servis çalışıyor mu?
curl http://localhost:11434/api/tags

# Çalışmıyorsa başlat
ollama serve
```

### GPU kullanılmıyor

```bash
# GPU görünüyor mu?
nvidia-smi

# Ollama logları
journalctl -u ollama -f
```

## 📁 Proje Yapısı

```
backend/
├── app/                       # Ana uygulama
│   ├── __init__.py
│   ├── main.py                # FastAPI giriş noktası
│   ├── config.py              # .env'den ayarlar
│   ├── database.py            # SQLAlchemy
│   ├── models/                # Veritabanı modelleri
│   │   ├── question.py
│   │   ├── test_run.py
│   │   ├── model_response.py
│   │   ├── evaluation.py
│   │   └── manual_label.py
│   ├── schemas/               # Pydantic şemaları
│   │   └── question.py
│   ├── services/              # İş mantığı
│   │   └── question_loader.py
│   └── routes/                # API endpoint'leri
│       ├── health.py
│       └── questions.py
├── data/
│   └── halusinasyon_test_sorulari.json  # 150 soruluk test seti
├── logs/                      # Log dosyaları (otomatik oluşturulur)
├── scripts/                   # Yardımcı scriptler
│   ├── setup.sh
│   ├── start.sh
│   └── check_system.sh
├── tests/                     # Pytest testleri (Aşama 7)
├── .env.example               # Ortam değişkenleri şablonu
├── .gitignore
├── requirements.txt
└── README.md
```

## 🎓 Akademik Bilgi

Bu proje **TR-Dizin** kapsamında akademik bir makaleye dönüştürülecektir. Bu nedenle:

- **Reproducibility:** Her test çalıştırması için kullanılan model versiyonları (SHA-256 digest), parametreler ve soru seti hash'i kayıt altına alınır.
- **UTC zaman damgası:** Tüm tarihler UTC olarak saklanır.
- **Açık kaynak:** Kod CC-BY lisansı ile yayımlanacaktır.

## 👥 Ekip

- **Atakan** - Backend geliştirme
- **Mehmet Sönmez** - Frontend geliştirme
- **Ahmet Ali Yılmaz** - Backend test/DevOps
- **Sevda Tuba Ehlibeyt** - Araştırma & istatistik analizi
- **Esad Abdullah Kösedağ** - Scrum Master

## 📄 Lisans

CC-BY 4.0 (yayım sonrası)

---

📧 Sorular için: [GitHub Issues](https://github.com/Atakan/LLM_hall/issues)
