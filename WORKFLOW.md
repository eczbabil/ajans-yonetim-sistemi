# 🔄 Günlük Çalışma Workflow'u

Bu dokümant, Flask uygulamanızı günlük olarak nasıl güncelleyeceğinizi ve PythonAnywhere'de canlıya alacağınızı gösterir.

## 🎯 Basit Workflow (2 Tık!)

### Adım 1: PC'de Değişiklik Yapın
1. Kodda değişiklik yapın (templates, app.py, CSS, vb.)
2. Dosyaları kaydedin (Ctrl+S)

### Adım 2: GitHub'a Gönderin ⚡
1. `sync.bat` dosyasına **çift tıklayın**
2. Commit mesajı yazın veya Enter (otomatik mesaj)
3. Window kapanınca GitHub'a gönderilmiş demektir ✅

### Adım 3: PythonAnywhere'de Güncelleyin 🌐
1. **Web** tab'ını açın: [pythonanywhere.com/user/oguzhandiscioglu/webapps](https://www.pythonanywhere.com/user/oguzhandiscioglu/webapps)
2. Yeşil **"Reload oguzhandiscioglu.pythonanywhere.com"** butonuna tıklayın
3. 5-10 saniye bekleyin

### Adım 4: Kontrol Edin ✅
1. Tarayıcıda: `https://oguzhandiscioglu.pythonanywhere.com`
2. Sayfayı yenileyin (Ctrl+Shift+R)
3. Değişikliklerinizi görün! 🎉

**TOPLAM SÜRE: ~30 saniye**

---

## 📁 Dosya Açıklamaları

### sync.bat (PC'de)
**Konum:** `ajans_yonetim_sistemi/sync.bat`

**Ne yapar:**
- Tüm değişiklikleri Git'e ekler (`git add .`)
- Commit oluşturur (mesaj sorar veya otomatik)
- GitHub'a push yapar (`git push`)
- Sonraki adımı hatırlatır

**Kullanımı:**
- Dosyaya **çift tıklayın**
- Commit mesajı yazın (veya Enter)
- Bekleyin (5-10 saniye)
- ✅ Tamamlandı!

---

## 🔧 Detaylı Komutlar (İsteğe Bağlı)

### Manuel Git Kullanımı

**PC'de PowerShell veya CMD:**

```bash
cd C:\Users\PC1\Desktop\Media\Media\ajans_yonetim_sistemi

# Değişiklikleri görün
git status

# Değişiklikleri ekle
git add .

# Commit
git commit -m "Değişiklik açıklaması"

# GitHub'a gönder
git push
```

### PythonAnywhere'de Manuel Güncelleme

**Bash Console:**

```bash
cd ~/ajans-yonetim-sistemi
git pull origin main
```

**Web Tab:**
- **Reload** butonuna tık

---

## 🚀 İleri Seviye: Branch Kullanımı

### Development Branch ile Çalışma

**Yeni özellik geliştirirken:**

```bash
# Development branch oluştur
git checkout -b development

# Değişiklikler yap
# ...

# Commit ve push
git add .
git commit -m "Yeni özellik: CRM iyileştirmeleri"
git push origin development
```

**Test sonrası main'e merge:**

```bash
git checkout main
git merge development
git push origin main
```

---

## 📊 Sık Kullanılan Senaryolar

### Senaryo 1: Dashboard'da Küçük Değişiklik

**Durum:** KPI kartının rengini değiştirmek istiyorsunuz.

**Adımlar:**
1. `static/css/modern.css` dosyasını düzenleyin
2. `sync.bat` çift tık
3. PythonAnywhere → Reload
4. ✅ Değişiklik canlıda!

**Süre:** ~30 saniye

---

### Senaryo 2: Yeni Sayfa Ekleme

**Durum:** Yeni bir "Raporlar" sayfası eklemek istiyorsunuz.

**Adımlar:**
1. `app.py`'ye yeni route ekleyin
2. `templates/raporlar.html` oluşturun
3. `base.html`'de navbar'a link ekleyin
4. Lokal test edin: `http://localhost:5000/raporlar`
5. `sync.bat` çift tık
6. PythonAnywhere → Reload
7. ✅ Yeni sayfa canlıda!

**Süre:** Geliştirme + ~30 saniye deployment

---

### Senaryo 3: Veritabanı Şeması Değişikliği

**Durum:** Müşteri modeline yeni alan eklemek istiyorsunuz.

**Adımlar:**
1. `app.py`'de model güncelleyin
2. Lokal test: Veritabanını sıfırlayın veya migration kullanın
3. `sync.bat` çift tık
4. PythonAnywhere Bash:
   ```bash
   cd ~/ajans-yonetim-sistemi
   git pull
   # Veritabanını yedekleyin!
   cp instance/ajans.db instance/ajans_backup.db
   # Yeni tabloları ekleyin
   python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```
5. Web tab → Reload
6. ✅ Şema değişikliği canlıda!

**⚠️ DİKKAT:** Veritabanı değişikliklerinde dikkatli olun!

---

## ⚠️ Dikkat Edilmesi Gerekenler

### .env Dosyası
- ❌ .env asla Git'e eklenmez (.gitignore'da)
- ✅ Her ortamda (PC, PythonAnywhere) ayrı .env olmalı
- ✅ Hassas bilgiler (SECRET_KEY, şifreler) .env'de

### Veritabanı
- ❌ `instance/ajans.db` Git'e eklenmez
- ✅ PythonAnywhere'de ayrı veritabanı
- ✅ Düzenli yedekleme yapın

### Uploads Klasörü
- ❌ `uploads/` içeriği Git'e eklenmez
- ✅ Her ortamda ayrı upload dosyaları
- ✅ Önemli dosyaları manuel yedekleyin

---

## 🐛 Sorun Giderme

### Problem: sync.bat çalışmıyor

**Çözüm:**
```bash
# Git PATH'e ekli mi kontrol edin
git --version

# PATH'e ekli değilse, PowerShell'de:
$env:Path += ";C:\Program Files\Git\cmd"
```

### Problem: PythonAnywhere'de git pull hata veriyor

**Çözüm:**
```bash
# Bash console'da
cd ~/ajans-yonetim-sistemi
git status

# Lokal değişiklikler varsa
git stash
git pull
git stash pop
```

### Problem: Reload sonrası değişiklik görünmüyor

**Çözüm:**
1. Error log kontrol edin (Web tab → Error log)
2. Tarayıcı cache'i temizleyin (Ctrl+Shift+R)
3. WSGI dosyası doğru mu kontrol edin
4. Static files mapping doğru mu kontrol edin

### Problem: Veritabanı hatası

**Çözüm:**
```bash
# PythonAnywhere Bash
cd ~/ajans-yonetim-sistemi
chmod 755 instance
ls -la instance/
```

---

## 📞 Yardım Kaynakları

### Dokümantasyon
- `README.md` - Genel kullanım
- `DEPLOYMENT.md` - PythonAnywhere kurulum
- `WORKFLOW.md` - Bu dosya

### Online Kaynaklar
- PythonAnywhere Help: [help.pythonanywhere.com](https://help.pythonanywhere.com)
- Flask Docs: [flask.palletsprojects.com](https://flask.palletsprojects.com)
- Git Guide: [git-scm.com/doc](https://git-scm.com/doc)

### Log Dosyaları
- PythonAnywhere Error Log: Web tab → Error log
- Server Log: Web tab → Server log
- Uygulama Log: `logs/ajans_*.log`

---

## 🎊 Özet

**En basit workflow:**

```
1. PC'de kod yaz
2. sync.bat çift tık
3. PythonAnywhere Reload tık
4. Bitti! ✅
```

**Hepsi bu kadar! 2 tık, 30 saniye!** ⚡

---

© 2025 Sisyphos Media & Design


