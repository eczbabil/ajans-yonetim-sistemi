# Sisyphos Ajans Yönetim Sistemi - Deployment Rehberi

Bu dokümant, Flask uygulamasını **PythonAnywhere**'e deploy etmek için adım adım talimatlar içerir.

## 📋 İçindekiler

1. [PythonAnywhere Hesabı](#pythonanywhere-hesabı)
2. [Dosyaları Yükleme](#dosyaları-yükleme)
3. [Virtual Environment Kurulumu](#virtual-environment-kurulumu)
4. [Veritabanı Kurulumu](#veritabanı-kurulumu)
5. [Web App Yapılandırması](#web-app-yapılandırması)
6. [Static Dosyalar](#static-dosyalar)
7. [Environment Variables](#environment-variables)
8. [Test ve Debugging](#test-ve-debugging)
9. [Güncelleme](#güncelleme)

---

## 1. PythonAnywhere Hesabı

### Adım 1.1: Hesap Oluşturma
1. [PythonAnywhere](https://www.pythonanywhere.com) adresine gidin
2. **Ücretsiz hesap** oluşturun (Beginner account yeterli)
3. Email doğrulaması yapın
4. Dashboard'a giriş yapın

### Adım 1.2: Hesap Bilgileri
- **Username**: `yourusername` (örnek: sisyphosajans)
- **Domain**: `yourusername.pythonanywhere.com`
- **Python Version**: Python 3.10 (önerilen)

---

## 2. Dosyaları Yükleme

### Seçenek A: Git ile (Önerilen)

```bash
# PythonAnywhere Bash Console'da
cd ~
git clone https://github.com/yourusername/ajans_yonetim_sistemi.git
```

### Seçenek B: Manuel Yükleme

1. **Files** sekmesine gidin
2. **Upload a file** butonuna tıklayın
3. Tüm proje dosyalarını yükleyin:
   - `app.py`
   - `wsgi.py`
   - `logger_config.py`
   - `requirements.txt`
   - `src/` klasörü (tüm içeriği)
   - `templates/` klasörü (tüm içeriği)
   - `static/` klasörü (tüm içeriği)

### Seçenek C: ZIP Dosyası

```bash
# PythonAnywhere Bash Console'da
cd ~
unzip ajans_yonetim_sistemi.zip
```

**Proje Dizini**: `/home/yourusername/ajans_yonetim_sistemi`

---

## 3. Virtual Environment Kurulumu

### Adım 3.1: Virtual Environment Oluşturma

PythonAnywhere **Bash Console** açın:

```bash
cd ~/ajans_yonetim_sistemi
python3.10 -m venv .venv
source .venv/bin/activate
```

### Adım 3.2: Paketleri Kurma

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Kurulum Süresi**: ~2-3 dakika

### Adım 3.3: Kurulum Doğrulama

```bash
python -c "import flask; print(flask.__version__)"
python -c "import pandas; print(pandas.__version__)"
```

---

## 4. Veritabanı Kurulumu

### Adım 4.1: Environment Variables Ayarlama

```bash
cd ~/ajans_yonetim_sistemi
cp env.example .env
nano .env
```

**.env içeriği:**

```bash
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
FLASK_ENV=production
DEBUG=False
DATABASE_URI=sqlite:////home/yourusername/ajans_yonetim_sistemi/instance/ajans.db
UPLOAD_FOLDER=/home/yourusername/ajans_yonetim_sistemi/uploads
SQLALCHEMY_TRACK_MODIFICATIONS=False
LOG_LEVEL=INFO
```

**⚠️ ÖNEMLİ**: 
- `yourusername` kısmını kendi kullanıcı adınızla değiştirin
- `SECRET_KEY` için güçlü, rastgele bir değer kullanın

### Adım 4.2: Klasörleri Oluşturma

```bash
mkdir -p instance
mkdir -p uploads
mkdir -p logs
chmod 755 instance uploads logs
```

### Adım 4.3: Veritabanını İlk Kez Oluşturma

```bash
source .venv/bin/activate
python3 << END
from app import app, db
with app.app_context():
    db.create_all()
    print("Veritabanı başarıyla oluşturuldu!")
END
```

**Kontrol:**
```bash
ls -lh instance/ajans.db
```

---

## 5. Web App Yapılandırması

### Adım 5.1: Web App Oluşturma

1. **Web** sekmesine gidin
2. **Add a new web app** butonuna tıklayın
3. **Manual configuration** seçin
4. **Python 3.10** seçin
5. **Next** butonuna tıklayın

### Adım 5.2: WSGI Dosyası Yapılandırması

1. **Web** sekmesinde **WSGI configuration file** linkine tıklayın
2. Tüm içeriği silin
3. Aşağıdaki kodu yapıştırın:

```python
import sys
import os

# Proje yolunu ekle
project_home = '/home/yourusername/ajans_yonetim_sistemi'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Environment variables yükle
from dotenv import load_dotenv
dotenv_path = os.path.join(project_home, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Flask uygulamasını import et
from app import app as application
```

**⚠️ ÖNEMLİ**: `yourusername` kısmını değiştirin!

4. **Save** butonuna tıklayın

### Adım 5.3: Virtualenv Ayarlama

1. **Web** sekmesine dönün
2. **Virtualenv** bölümüne gidin
3. Path girin: `/home/yourusername/ajans_yonetim_sistemi/.venv`

---

## 6. Static Dosyalar

### Adım 6.1: Static Files Mapping

**Web** sekmesinde **Static files** bölümüne:

| URL                  | Directory                                                    |
|----------------------|--------------------------------------------------------------|
| `/static`            | `/home/yourusername/ajans_yonetim_sistemi/static`          |
| `/static/css`        | `/home/yourusername/ajans_yonetim_sistemi/static/css`      |
| `/static/js`         | `/home/yourusername/ajans_yonetim_sistemi/static/js`       |
| `/static/images`     | `/home/yourusername/ajans_yonetim_sistemi/static/images`   |

### Adım 6.2: Upload Folder İzinleri

```bash
chmod 755 /home/yourusername/ajans_yonetim_sistemi/uploads
```

---

## 7. Environment Variables

### Üretim için Güvenlik Ayarları

**.env dosyasında:**

```bash
# Güçlü SECRET_KEY oluşturma:
python3 -c "import secrets; print(secrets.token_hex(32))"

# .env'e ekleyin:
SECRET_KEY=yukarıdaki-çıktıyı-buraya-yapıştırın
```

**Güvenlik Kontrol Listesi:**
- ✅ SECRET_KEY değiştirildi
- ✅ DEBUG=False
- ✅ Veritabanı yolu mutlak
- ✅ Upload folder yolu mutlak

---

## 8. Test ve Debugging

### Adım 8.1: Web App'i Başlatma

1. **Web** sekmesinde **Reload** butonuna tıklayın
2. Site adresinize gidin: `https://yourusername.pythonanywhere.com`

### Adım 8.2: Hata Ayıklama

**Error log kontrolü:**

1. **Web** sekmesinde **Error log** linkine tıklayın
2. Son satırları okuyun

**Yaygın Hatalar ve Çözümleri:**

#### Hata: "No module named 'flask'"
```bash
source ~/ajans_yonetim_sistemi/.venv/bin/activate
pip install -r requirements.txt
```

#### Hata: "Unable to open database file"
```bash
chmod 755 ~/ajans_yonetim_sistemi/instance
chmod 666 ~/ajans_yonetim_sistemi/instance/ajans.db
```

#### Hata: "Static files not loading"
- Static files mapping'i kontrol edin
- Dosya izinlerini kontrol edin: `chmod 755 static/`

### Adım 8.3: Manuel Test

```bash
cd ~/ajans_yonetim_sistemi
source .venv/bin/activate
python3
```

```python
from app import app, db
with app.app_context():
    from app import Musteri
    print(Musteri.query.count())  # Müşteri sayısını göster
```

---

## 9. Güncelleme

### Git ile Güncelleme

```bash
cd ~/ajans_yonetim_sistemi
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
# Web sekmesinde Reload butonuna tıklayın
```

### Manuel Güncelleme

1. Değişen dosyaları yükleyin
2. Bash console'da:
```bash
cd ~/ajans_yonetim_sistemi
source .venv/bin/activate
# Gerekirse paketleri güncelleyin
pip install -r requirements.txt
```
3. **Web** sekmesinde **Reload** butonuna tıklayın

---

## 🎉 Başarılı Deployment!

Uygulamanız artık canlıda: `https://yourusername.pythonanywhere.com`

### İlk Giriş Sonrası:

1. ✅ Dashboard'u kontrol edin
2. ✅ İlk müşteriyi ekleyin
3. ✅ Tüm sayfaları test edin
4. ✅ Excel import/export'u test edin

---

## 📞 Destek ve Sorun Giderme

### PythonAnywhere Forumları
- https://www.pythonanywhere.com/forums/

### Uygulamanızın Logları
- Error log: `/var/log/yourusername.pythonanywhere.com.error.log`
- Server log: `/var/log/yourusername.pythonanywhere.com.server.log`

### Bash Console Komutları

```bash
# Log dosyalarını görüntüleme
tail -f ~/ajans_yonetim_sistemi/logs/ajans_*.log

# Veritabanını yedekleme
cp ~/ajans_yonetim_sistemi/instance/ajans.db ~/ajans_backup_$(date +%Y%m%d).db

# Disk kullanımı
du -sh ~/ajans_yonetim_sistemi
```

---

## 🔒 Güvenlik Notları

1. **SECRET_KEY**: Mutlaka değiştirin ve güçlü yapın
2. **.env dosyası**: Asla git'e eklemeyin
3. **Database**: Düzenli yedekleyin
4. **Uploads**: Dosya türü kontrolü yapın
5. **HTTPS**: PythonAnywhere otomatik sağlıyor

---

## 📊 Performans İpuçları

### Ücretsiz Plan Limitleri:
- CPU: Günlük 100 saniye
- Disk: 512 MB
- Bandwidth: Sınırsız (yavaşlama olabilir)

### Optimizasyon:
- Gereksiz logları azaltın
- Veritabanı sorgularını optimize edin
- Static dosyaları sıkıştırın

---

**© 2025 Sisyphos Media & Design**



