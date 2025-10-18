# 🏢 Sisyphos Ajans Yönetim Sistemi

Modern ve kapsamlı ajans yönetim sistemi. Flask backend, modern UI/UX, dashboard, CRM modülü ve PythonAnywhere deployment desteği.

## ✨ Özellikler

### 📊 Modern Dashboard
- **KPI Kartları**: Toplam müşteri, bu ay iş sayısı, onaylanan teslimatlar, toplam çalışma saati
- **Canlı Grafikler**: İş tipi dağılımı, günlük iş adedi, kişi başı katkı, teslimat durumları
- **Responsive Tasarım**: Mobil uyumlu, modern UI
- **Chart.js Entegrasyonu**: İnteraktif grafikler

### 👥 Müşteri Yönetimi
- Otomatik müşteri kodu (MST001, MST002, ...)
- Müşteri detay sayfaları
- Sözleşme ve ödeme takibi
- İlgili kişi ve iletişim bilgileri

### 📝 İş Günlüğü
- İş kaydı ve takip
- Süre hesaplama (dakika/saat)
- Aktivite türü bazlı raporlama
- Etiketleme sistemi

### 📦 Teslimat Yönetimi
- Otomatik teslimat kodu (TSLMST001001, ...)
- Durum takibi (Hazırlanıyor, Onaylandı, Revizede)
- Teslim tarihi yönetimi
- Müşteri bazlı teslimat listesi

### 📱 Sosyal Medya Takibi
- Platform bazlı içerik yönetimi (Instagram, Facebook, LinkedIn, YouTube)
- Gönderi türü (Reels, Post, Story)
- Etkileşim metrikleri (görüntülenme, beğeni, yorum, paylaşım)
- Performans analizi

### ☎️ CRM - Arama Kayıtları (YENİ!)
- Müşteri arama kayıtları
- Geri dönüş takibi
- Sonuç ve durum yönetimi
- Hatırlatıcı sistemi

### 🔄 Revizyon Yönetimi
- Revizyon talep takibi
- Teslimat bağlantılı revizyonlar
- Durum güncelleme

### 📊 Excel Import/Export
- Müşteri verilerini Excel'den içe aktarma
- Tüm verileri Excel'e dışa aktarma
- Çoklu sayfa (Müşteriler, İş Günlüğü, Teslimatlar, Sosyal Medya)

## 🎨 Arayüz Özellikleri

### Modern UI Bileşenleri
- **KPI Cards**: Gradient arka plan, hover efekti, ikonlu başlıklar
- **Badge System**: Renkli durum göstergeleri (yeşil=ok, sarı=wait, kırmızı=warn)
- **Modern Buttons**: Rounded corners, hover animasyonları
- **Responsive Tables**: Mobil uyumlu, hover efektli satırlar
- **Chart Containers**: Gölgeli, rounded chart alanları

### Renk Paleti
- **Primary**: #2563eb (Mavi)
- **Success**: #10b981 (Yeşil)
- **Warning**: #f59e0b (Sarı)
- **Danger**: #ef4444 (Kırmızı)
- **Info**: #0ea5e9 (Açık Mavi)

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- pip
- SQLite

### Lokal Kurulum

```bash
# Projeyi klonlayın
git clone https://github.com/yourusername/ajans_yonetim_sistemi.git
cd ajans_yonetim_sistemi

# Virtual environment oluşturun
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# Paketleri yükleyin
pip install -r requirements.txt

# Environment variables ayarlayın
cp env.example .env
# .env dosyasını düzenleyin

# Uygulamayı çalıştırın
python app.py
```

Tarayıcıda: `http://localhost:5000`

## 🌍 PythonAnywhere Deployment

Detaylı talimatlar için: **[DEPLOYMENT.md](DEPLOYMENT.md)**

### Hızlı Başlangıç

```bash
# PythonAnywhere Bash Console
cd ~
git clone https://github.com/yourusername/ajans_yonetim_sistemi.git
cd ajans_yonetim_sistemi
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Environment variables
cp env.example .env
nano .env  # SECRET_KEY ve yolları düzenleyin

# Veritabanı oluştur
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

Web app yapılandırması ve WSGI ayarları için [DEPLOYMENT.md](DEPLOYMENT.md) dosyasını okuyun.

## 📁 Proje Yapısı

```
ajans_yonetim_sistemi/
├── app.py                    # Ana Flask uygulaması
├── wsgi.py                   # PythonAnywhere WSGI
├── logger_config.py          # Logger yapılandırması
├── requirements.txt          # Python paketleri
├── env.example               # Environment variables şablonu
├── DEPLOYMENT.md             # Deployment rehberi
├── README.md                 # Bu dosya
├── src/
│   ├── models/               # Veritabanı modelleri
│   │   ├── arama.py         # CRM - Arama kayıtları
│   │   ├── is_gunlugu.py
│   │   ├── musteri.py
│   │   ├── revizyon.py
│   │   ├── sosyal_medya.py
│   │   └── teslimat.py
│   ├── routes/               # Route handlers (şu an app.py'de)
│   └── utils/
│       ├── database.py
│       ├── helpers.py
│       └── statistics.py     # Dashboard metrikleri
├── static/
│   ├── css/
│   │   └── modern.css       # Modern UI stilleri
│   ├── js/
│   │   └── charts.js        # Chart.js utilities
│   └── images/
├── templates/
│   ├── base.html            # Ana template
│   ├── dashboard.html       # Modern dashboard
│   ├── aramalar.html        # CRM - Arama listesi
│   ├── arama_ekle.html      # CRM - Arama formu
│   ├── musteriler.html
│   ├── musteri_detay.html
│   ├── musteri_ekle.html
│   ├── is_gunlugu.html
│   ├── is_ekle.html
│   ├── teslimatlar.html
│   ├── teslimat_ekle.html
│   ├── sosyal_medya.html
│   ├── sosyal_medya_ekle.html
│   ├── revizyon_ekle.html
│   ├── excel_import.html
│   └── index.html
├── instance/
│   └── ajans.db             # SQLite veritabanı
├── uploads/                  # Yüklenen dosyalar
└── logs/                     # Log dosyaları
```

## 🔧 Teknolojiler

### Backend
- **Flask 2.3.3**: Web framework
- **SQLAlchemy 2.0.23**: ORM
- **Pandas 1.5.3**: Veri işleme
- **python-dotenv**: Environment variables

### Frontend
- **Bootstrap 5**: UI framework
- **Chart.js 4.4**: Grafikler
- **Bootstrap Icons**: İkonlar
- **Custom CSS**: Modern tasarım

### Veritabanı
- **SQLite**: Hafif, dosya tabanlı DB

## 📊 Veritabanı Modelleri

### Musteri
- Otomatik kod: MST001, MST002, ...
- İlişkiler: IsGunlugu, Teslimat, SosyalMedya, Revizyon, Arama

### IsGunlugu
- Aktivite türü, süre (dakika), tarih
- Foreign Key: musteri_id

### Teslimat
- Otomatik kod: TSLMST001001
- Durum: Hazırlanıyor, Onaylandı, Revizede
- Foreign Key: musteri_id

### SosyalMedya
- Platform, gönderi türü, metrikler
- Foreign Key: musteri_id

### Revizyon
- Revizyon takibi
- Foreign Keys: musteri_id, teslimat_id

### Arama (YENİ!)
- CRM arama kayıtları
- Geri dönüş tarihi, sonuç, durum
- Foreign Key: musteri_id

## 🎯 Kullanım

### Dashboard
- Ana sayfada tüm metrikleri görüntüleyin
- Grafiklerle performans analizi yapın
- Hızlı erişim kartlarıyla sayfalara gidin

### Müşteri Ekleme
1. Navbar > Müşteriler > Yeni Müşteri
2. Formu doldurun (otomatik kod oluşturulur)
3. Kaydet

### İş Günlüğü Ekleme
1. Navbar > İş Günlüğü > Yeni İş
2. Müşteri seçin, detayları girin
3. Süre (dakika) girin
4. Kaydet

### CRM - Arama Kaydı
1. Navbar > Aramalar > Yeni Arama Kaydı
2. Müşteri ve arama detayları
3. Geri dönüş tarihi belirtin (opsiyonel)
4. Kaydet

### Excel Import
1. Navbar > Ayarlar > Excel İçe Aktar
2. .xlsx dosyası yükleyin
3. Veriler otomatik içe aktarılır

## 🔒 Güvenlik

### Production Ortamı İçin
1. **SECRET_KEY**: Güçlü, rastgele değer kullanın
   ```python
   import secrets
   secrets.token_hex(32)
   ```
2. **DEBUG=False**: .env dosyasında
3. **HTTPS**: PythonAnywhere otomatik sağlıyor
4. **Database Backup**: Düzenli yedekleme yapın

## 📝 Geliştirme Notları

### Yeni Özellikler Ekleme

1. **Yeni Model**: `src/models/` altında oluşturun
2. **Yeni Route**: `app.py`'ye ekleyin (veya `src/routes/` modülerleştirin)
3. **Yeni Template**: `templates/` altında `base.html`'i extend edin
4. **Navbar Güncellemesi**: `base.html`'de nav linklerini ekleyin

### Stil Değişiklikleri

- **KPI Kartları**: `static/css/modern.css` > `.kpi-card`
- **Renkler**: `:root` CSS variables
- **Grafikler**: `static/js/charts.js`

## 🐛 Sorun Giderme

### Veritabanı Hatası
```bash
# Veritabanını sıfırla
rm instance/ajans.db
python app.py  # Otomatik oluşturulur
```

### Import Hatası
```bash
# Paketleri yeniden yükle
pip install -r requirements.txt --force-reinstall
```

### Static Dosyalar Yüklenmiyor
- Browser cache'i temizleyin (Ctrl+Shift+R)
- `static/` klasör izinlerini kontrol edin

## 📞 Destek

- **Email**: info@sisyphosmedia.com
- **GitHub Issues**: [github.com/yourusername/ajans_yonetim_sistemi/issues](https://github.com)
- **PythonAnywhere Forum**: [pythonanywhere.com/forums](https://www.pythonanywhere.com/forums/)

## 📄 Lisans

© 2025 Sisyphos Media & Design. Tüm hakları saklıdır.

---

**Geliştirici**: Sisyphos Media & Design Team  
**Versiyon**: 2.0 (Modernized)  
**Son Güncelleme**: Ekim 2025


