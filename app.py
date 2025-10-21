from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import pandas as pd
import os
from werkzeug.utils import secure_filename
from logger_config import setup_logger
from dotenv import load_dotenv

# Environment variables yükle
load_dotenv()

app = Flask(__name__)

# Yapılandırma - Environment variables'dan veya varsayılan değerler
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sisyphos_ajans_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///ajans.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

# PythonAnywhere için mutlak yollar
if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:////'):
    # Relative path ise mutlak yola çevir
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            basedir = os.path.abspath(os.path.dirname(__file__))
            instance_path = os.path.join(basedir, 'instance')
            os.makedirs(instance_path, exist_ok=True)
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, db_path)}'

# Upload folder için mutlak yol
if not os.path.isabs(app.config['UPLOAD_FOLDER']):
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# Logger'ı kur
logger = setup_logger(app)

# Veritabanı modelleri
class Musteri(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    musteri_kodu = db.Column(db.String(20), unique=True)  # MST-001, MST-002, etc.
    ad = db.Column(db.String(100), nullable=False)
    sektor = db.Column(db.String(50))
    sozlesme_baslangic = db.Column(db.Date)
    aylik_ucret = db.Column(db.Float)
    ilgil_kisi = db.Column(db.String(100))
    telefon = db.Column(db.String(20))
    email = db.Column(db.String(100))
    notlar = db.Column(db.Text)

class IsGunlugu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_kodu = db.Column(db.String(30), unique=True)  # MST001-IS001, MST001-IS002
    tarih = db.Column(db.Date, nullable=False)
    musteri_id = db.Column(db.Integer, db.ForeignKey('musteri.id'))
    proje = db.Column(db.String(100))
    aktivite_turu = db.Column(db.String(50))
    aciklama = db.Column(db.Text)
    sorumlu_kisi = db.Column(db.String(100))
    sure_dakika = db.Column(db.Integer)
    etiketler = db.Column(db.String(200))
    durum = db.Column(db.String(20), default='Bekliyor')  # Bekliyor, Revizede, Onayda, Onaylandı, Reddedildi
    revizyon_sayisi = db.Column(db.Integer, default=0)  # Kaç revizyon yapıldı

class Teslimat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    musteri_id = db.Column(db.Integer, db.ForeignKey('musteri.id'))
    is_gunlugu_id = db.Column(db.Integer, db.ForeignKey('is_gunlugu.id'), nullable=False)  # ZORUNLU - Her teslimat bir işten gelir
    aktivite_turu = db.Column(db.String(50))
    proje = db.Column(db.String(100))
    teslim_turu = db.Column(db.String(50))  # Sosyal Medya / Konvensiyonel / Diğer
    baslik = db.Column(db.String(100))
    sorumlu_kisi = db.Column(db.String(100))
    olusturma_tarihi = db.Column(db.Date)
    teslim_tarihi = db.Column(db.Date)
    durum = db.Column(db.String(20))
    aciklama = db.Column(db.Text)
    
    # Sosyal Medya Alanları (sadece teslim_turu="Sosyal Medya" ise doldurulur)
    platform = db.Column(db.String(50), nullable=True)  # Instagram, Facebook, Twitter, LinkedIn, TikTok, YouTube
    gonderi_turu = db.Column(db.String(50), nullable=True)  # Post, Reels, Story, Video, Fotoğraf, Carousel
    etkileşim = db.Column(db.Integer, nullable=True)
    goruntulenme = db.Column(db.Integer, nullable=True)
    begeni = db.Column(db.Integer, nullable=True)
    yorum = db.Column(db.Integer, nullable=True)
    paylasim = db.Column(db.Integer, nullable=True)

class SosyalMedya(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.Date, nullable=False)
    musteri_id = db.Column(db.Integer, db.ForeignKey('musteri.id'))
    is_gunlugu_id = db.Column(db.Integer, db.ForeignKey('is_gunlugu.id'), nullable=True)  # İş ile ilişki
    platform = db.Column(db.String(50))
    icerik_basligi = db.Column(db.String(100))
    gonderi_turu = db.Column(db.String(20))
    etkileşim = db.Column(db.Integer)
    goruntulenme = db.Column(db.Integer)
    begeni = db.Column(db.Integer)
    yorum = db.Column(db.Integer)
    paylasim = db.Column(db.Integer)
    durum = db.Column(db.String(20))

class Revizyon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.Date, nullable=False)
    musteri_id = db.Column(db.Integer, db.ForeignKey('musteri.id'))
    is_gunlugu_id = db.Column(db.Integer, db.ForeignKey('is_gunlugu.id'), nullable=True)  # İş ile ilişki
    revizyon_numarasi = db.Column(db.Integer, default=1)  # Revizyon 1, Revizyon 2, etc.
    baslik = db.Column(db.String(100))  # "Revizyon 1", "Revizyon 2", etc.
    revize_talep_eden = db.Column(db.String(100))
    revize_konusu = db.Column(db.Text)
    durum = db.Column(db.String(20), default='Bekliyor')

class Arama(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.Date, nullable=False)
    musteri_id = db.Column(db.Integer, db.ForeignKey('musteri.id'))
    arayan_aranan = db.Column(db.String(100))
    konu = db.Column(db.Text)
    sonuc = db.Column(db.String(50))
    sorumlu_kisi = db.Column(db.String(100))
    notlar = db.Column(db.Text)
    geri_donus_tarihi = db.Column(db.Date, nullable=True)
    durum = db.Column(db.String(20), default='Bekliyor')

# Yardımcı fonksiyonlar - ID oluşturma
def generate_musteri_kodu():
    """Yeni müşteri kodu oluştur: MST001, MST002, etc."""
    with app.app_context():
        son_musteri = Musteri.query.order_by(Musteri.id.desc()).first()
        if son_musteri and son_musteri.musteri_kodu:
            try:
                son_numara = int(son_musteri.musteri_kodu.replace('MST', ''))
                yeni_numara = son_numara + 1
            except:
                yeni_numara = 1
        else:
            yeni_numara = 1
        
        # Kodun unique olduğundan emin ol
        while True:
            yeni_kod = f"MST{yeni_numara:03d}"
            exists = Musteri.query.filter_by(musteri_kodu=yeni_kod).first()
            if not exists:
                return yeni_kod
            yeni_numara += 1

def generate_teslimat_kodu(musteri):
    """Yeni teslimat kodu oluştur: TSLMST001001, TSLMST001002, etc."""
    if not musteri or not musteri.musteri_kodu:
        return f"TSLUNKNOWN001"
    
    with app.app_context():
        # Müşteri kodunu al (zaten tire yok)
        musteri_kod = musteri.musteri_kodu
        
        # Bu müşterinin son teslimatını bul
        son_teslimat = Teslimat.query.filter_by(musteri_id=musteri.id).order_by(Teslimat.id.desc()).first()
        
        if son_teslimat and son_teslimat.teslimat_kodu:
            try:
                # Son 3 karakteri al (teslimat sıra numarası)
                son_numara = int(son_teslimat.teslimat_kodu[-3:])
                yeni_numara = son_numara + 1
            except:
                yeni_numara = 1
        else:
            yeni_numara = 1
        
        # Kodun unique olduğundan emin ol
        while True:
            yeni_kod = f"TSL{musteri_kod}{yeni_numara:03d}"
            exists = Teslimat.query.filter_by(teslimat_kodu=yeni_kod).first()
            if not exists:
                return yeni_kod
            yeni_numara += 1

def generate_is_kodu(musteri):
    """Yeni iş kodu oluştur: MST001-IS001, MST001-IS002, etc."""
    if not musteri or not musteri.musteri_kodu:
        return f"UNKNOWN-IS001"
    
    with app.app_context():
        # Müşteri kodunu al
        musteri_kod = musteri.musteri_kodu
        
        # Bu müşterinin son işini bul
        son_is = IsGunlugu.query.filter_by(musteri_id=musteri.id).order_by(IsGunlugu.id.desc()).first()
        
        if son_is and son_is.is_kodu:
            try:
                # Son 3 karakteri al (iş sıra numarası)
                son_numara = int(son_is.is_kodu.split('-IS')[-1])
                yeni_numara = son_numara + 1
            except:
                yeni_numara = 1
        else:
            yeni_numara = 1
        
        # Kodun unique olduğundan emin ol
        while True:
            yeni_kod = f"{musteri_kod}-IS{yeni_numara:03d}"
            exists = IsGunlugu.query.filter_by(is_kodu=yeni_kod).first()
            if not exists:
                return yeni_kod
            yeni_numara += 1

# Ana sayfa - Modern Dashboard
@app.route('/')
def index():
    from src.utils.statistics import (
        get_dashboard_metrics,
        get_is_tipi_dagilimi,
        get_gunluk_is_adedi,
        get_kisi_basi_is_sayisi,
        get_teslimat_durum_dagilimi
    )
    
    # Dashboard metrikleri
    metrics = get_dashboard_metrics(db)
    
    # Grafikler için veri
    is_tipi_dag = get_is_tipi_dagilimi(db)
    gunluk_is = get_gunluk_is_adedi(db, days=30)
    kisi_basi = get_kisi_basi_is_sayisi(db, limit=5)
    teslimat_durum = get_teslimat_durum_dagilimi(db)
    
    return render_template('dashboard.html',
                         metrics=metrics,
                         is_tipi_dagilimi=is_tipi_dag,
                         gunluk_is_adedi=gunluk_is,
                         kisi_basi_is=kisi_basi,
                         teslimat_durum=teslimat_durum)

# Müşteri yönetimi
@app.route('/musteriler')
def musteriler():
    musteriler = Musteri.query.all()
    return render_template('musteriler.html', musteriler=musteriler)

# Müşteri detay sayfası
@app.route('/musteri_detay/<int:musteri_id>')
def musteri_detay(musteri_id):
    from src.utils.statistics import get_musteri_metrikleri
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    musteri = Musteri.query.get_or_404(musteri_id)
    
    # Filtre parametresi
    filtre = request.args.get('filtre', 'ay')
    today = datetime.now().date()
    
    # Tarih aralığını belirle
    if filtre == 'ay':
        start_date = datetime(today.year, today.month, 1).date()
        end_date = None
    elif filtre == 'yil':
        start_date = datetime(today.year, 1, 1).date()
        end_date = None
    elif filtre == '6ay':
        start_date = today - timedelta(days=180)
        end_date = None
    else:  # 'tumu'
        start_date = None
        end_date = None
    
    # Metrikleri hesapla
    metrikler = get_musteri_metrikleri(db, musteri_id, start_date, end_date)
    
    # Teslimatlar, sosyal medya, revizyonlar - filtreye göre
    teslimatlar_query = Teslimat.query.filter_by(musteri_id=musteri_id)
    sosyal_query = SosyalMedya.query.filter_by(musteri_id=musteri_id)
    revizyon_query = Revizyon.query.filter_by(musteri_id=musteri_id)
    is_gunlugu_query = IsGunlugu.query.filter_by(musteri_id=musteri_id)
    
    if start_date:
        teslimatlar_query = teslimatlar_query.filter(Teslimat.teslim_tarihi >= start_date)
        sosyal_query = sosyal_query.filter(SosyalMedya.tarih >= start_date)
        revizyon_query = revizyon_query.filter(Revizyon.tarih >= start_date)
        is_gunlugu_query = is_gunlugu_query.filter(IsGunlugu.tarih >= start_date)
    
    if end_date:
        teslimatlar_query = teslimatlar_query.filter(Teslimat.teslim_tarihi <= end_date)
        sosyal_query = sosyal_query.filter(SosyalMedya.tarih <= end_date)
        revizyon_query = revizyon_query.filter(Revizyon.tarih <= end_date)
        is_gunlugu_query = is_gunlugu_query.filter(IsGunlugu.tarih <= end_date)
    
    teslimatlar = teslimatlar_query.order_by(Teslimat.teslim_tarihi.desc()).all()
    sosyal_medyalar = sosyal_query.order_by(SosyalMedya.tarih.desc()).all()
    revizyonlar = revizyon_query.order_by(Revizyon.tarih.desc()).all()
    isler = is_gunlugu_query.order_by(IsGunlugu.tarih.desc()).all()
    
    # Onayda bekleyen işler
    onayda_bekleyenler_query = IsGunlugu.query.filter_by(musteri_id=musteri_id, durum='Onayda')
    if start_date:
        onayda_bekleyenler_query = onayda_bekleyenler_query.filter(IsGunlugu.tarih >= start_date)
    if end_date:
        onayda_bekleyenler_query = onayda_bekleyenler_query.filter(IsGunlugu.tarih <= end_date)
    onayda_bekleyenler = onayda_bekleyenler_query.order_by(IsGunlugu.tarih.desc()).all()
    
    # Revizyon sayısı artık her iş için ayrı takip ediliyor (is_gunlugu.revizyon_sayisi)
    
    # Dashboard İstatistikleri
    # 1. Toplam çalışma saati (iş günlüğünden)
    toplam_dakika = db.session.query(func.sum(IsGunlugu.sure_dakika))\
        .filter(IsGunlugu.musteri_id == musteri_id).scalar() or 0
    toplam_saat = toplam_dakika / 60
    
    # 2. Onaylanan teslimatlar
    onaylanan_teslimatlar = len([t for t in teslimatlar if t.durum in ['Tamamlandı', 'Teslim Edildi']])
    
    # 3. Devam eden teslimatlar
    devam_eden_teslimatlar = len([t for t in teslimatlar if t.durum == 'Hazırlanıyor'])
    
    # 4. Toplam iş sayısı
    toplam_is = len(isler)
    
    # 5. Toplam teslimat sayısı
    toplam_teslimat = len(teslimatlar)
    
    # 6. Sosyal medya teslimat sayısı
    sosyal_medya_teslimat = len([t for t in teslimatlar if t.teslim_turu == 'Sosyal Medya'])
    
    # Aramalar (varsa)
    try:
        aramalar = Arama.query.filter_by(musteri_id=musteri_id).order_by(Arama.tarih.desc()).limit(10).all()
    except:
        aramalar = []
    
    return render_template('musteri_detay.html',
                         musteri=musteri,
                         teslimatlar=teslimatlar,
                         sosyal_medyalar=sosyal_medyalar,
                         revizyonlar=revizyonlar,
                         isler=isler,
                         onayda_bekleyenler=onayda_bekleyenler,
                         aramalar=aramalar,
                         metrikler=metrikler,
                         filtre=filtre,
                         # Dashboard istatistikleri
                         toplam_saat=toplam_saat,
                         onaylanan_teslimatlar=onaylanan_teslimatlar,
                         devam_eden_teslimatlar=devam_eden_teslimatlar,
                         toplam_is=toplam_is,
                         toplam_teslimat=toplam_teslimat,
                         sosyal_medya_teslimat=sosyal_medya_teslimat)

@app.route('/musteri_rapor/<int:musteri_id>')
def musteri_rapor(musteri_id):
    """Müşteri raporlama sayfası - detaylı istatistikler"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    musteri = Musteri.query.get_or_404(musteri_id)
    
    # Filtre parametresi
    filtre = request.args.get('filtre', 'ay')
    today = datetime.now().date()
    
    # Tarih aralığını belirle
    if filtre == 'ay':
        start_date = datetime(today.year, today.month, 1).date()
        end_date = None
    elif filtre == 'yil':
        start_date = datetime(today.year, 1, 1).date()
        end_date = None
    elif filtre == '6ay':
        start_date = today - timedelta(days=180)
        end_date = None
    else:  # 'tumu'
        start_date = None
        end_date = None
    
    # Teslimatlar, revizyonlar, işler - filtreye göre
    teslimatlar_query = Teslimat.query.filter_by(musteri_id=musteri_id)
    revizyon_query = Revizyon.query.filter_by(musteri_id=musteri_id)
    is_gunlugu_query = IsGunlugu.query.filter_by(musteri_id=musteri_id)
    
    if start_date:
        teslimatlar_query = teslimatlar_query.filter(Teslimat.teslim_tarihi >= start_date)
        revizyon_query = revizyon_query.filter(Revizyon.tarih >= start_date)
        is_gunlugu_query = is_gunlugu_query.filter(IsGunlugu.tarih >= start_date)
    
    if end_date:
        teslimatlar_query = teslimatlar_query.filter(Teslimat.teslim_tarihi <= end_date)
        revizyon_query = revizyon_query.filter(Revizyon.tarih <= end_date)
        is_gunlugu_query = is_gunlugu_query.filter(IsGunlugu.tarih <= end_date)
    
    teslimatlar = teslimatlar_query.order_by(Teslimat.teslim_tarihi.desc()).all()
    revizyonlar = revizyon_query.order_by(Revizyon.tarih.desc()).all()
    isler = is_gunlugu_query.order_by(IsGunlugu.tarih.desc()).all()
    
    # Dashboard İstatistikleri
    # 1. Toplam çalışma saati (iş günlüğünden)
    toplam_dakika_query = db.session.query(func.sum(IsGunlugu.sure_dakika))\
        .filter(IsGunlugu.musteri_id == musteri_id)
    if start_date:
        toplam_dakika_query = toplam_dakika_query.filter(IsGunlugu.tarih >= start_date)
    if end_date:
        toplam_dakika_query = toplam_dakika_query.filter(IsGunlugu.tarih <= end_date)
    toplam_dakika = toplam_dakika_query.scalar() or 0
    toplam_saat = toplam_dakika / 60
    
    # 2. Onaylanan teslimatlar
    onaylanan_teslimatlar = len([t for t in teslimatlar if t.durum in ['Tamamlandı', 'Teslim Edildi']])
    
    # 3. Devam eden teslimatlar
    devam_eden_teslimatlar = len([t for t in teslimatlar if t.durum == 'Hazırlanıyor'])
    
    # 4. Toplam iş sayısı
    toplam_is = len(isler)
    
    # 5. Toplam teslimat sayısı
    toplam_teslimat = len(teslimatlar)
    
    # 6. Sosyal medya teslimat sayısı
    sosyal_medya_teslimat = len([t for t in teslimatlar if t.teslim_turu == 'Sosyal Medya'])
    
    # 7. Revizyon sayısı
    toplam_revizyon = len(revizyonlar)
    
    return render_template('musteri_rapor.html',
                         musteri=musteri,
                         teslimatlar=teslimatlar,
                         revizyonlar=revizyonlar,
                         isler=isler,
                         filtre=filtre,
                         # Dashboard istatistikleri
                         toplam_saat=toplam_saat,
                         onaylanan_teslimatlar=onaylanan_teslimatlar,
                         devam_eden_teslimatlar=devam_eden_teslimatlar,
                         toplam_is=toplam_is,
                         toplam_teslimat=toplam_teslimat,
                         sosyal_medya_teslimat=sosyal_medya_teslimat,
                         toplam_revizyon=toplam_revizyon)

@app.route('/musteri_ekle', methods=['GET', 'POST'])
def musteri_ekle():
    if request.method == 'POST':
        try:
            logger.info(f"Müşteri ekleme başladı - Ad: {request.form.get('ad')}")
            
            # Otomatik müşteri kodu oluştur
            musteri_kodu = generate_musteri_kodu()
            logger.info(f"Oluşturulan müşteri kodu: {musteri_kodu}")
            
            musteri = Musteri(
                musteri_kodu=musteri_kodu,
                ad=request.form['ad'],
                sektor=request.form['sektor'],
                sozlesme_baslangic=datetime.strptime(request.form['sozlesme_baslangic'], '%Y-%m-%d').date(),
                aylik_ucret=float(request.form['aylik_ucret'] or 0),
                ilgil_kisi=request.form['ilgili_kisi'],
                telefon=request.form['telefon'],
                email=request.form['email'],
                notlar=request.form['notlar'],
            )
            db.session.add(musteri)
            db.session.commit()
            logger.info(f"Müşteri başarıyla eklendi - Kod: {musteri.musteri_kodu}, Ad: {musteri.ad}")
            flash(f'Müşteri başarıyla eklendi! Müşteri Kodu: {musteri.musteri_kodu}')
            return redirect(url_for('musteriler'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Müşteri ekleme hatası: {str(e)}", exc_info=True)
            flash(f'Hata: {str(e)}', 'error')

    return render_template('musteri_ekle.html')

# İş günlüğü
@app.route('/is_gunlugu')
def is_gunlugu():
    isler = IsGunlugu.query.all()
    return render_template('is_gunlugu.html', isler=isler)

@app.route('/is_ekle', methods=['GET', 'POST'])
def is_ekle():
    musteriler = Musteri.query.all()
    if request.method == 'POST':
        try:
            # Müşteri bilgisini al
            musteri = Musteri.query.get(int(request.form['musteri_id']))
            if not musteri:
                flash('Müşteri bulunamadı!', 'error')
                return redirect(url_for('is_ekle'))
            
            # Otomatik iş kodu oluştur
            is_kodu = generate_is_kodu(musteri)
            logger.info(f"Oluşturulan iş kodu: {is_kodu}")
            
            # Saat ve dakikayı toplam dakikaya çevir
            sure_saat = int(request.form.get('sure_saat', 0))
            sure_dakika = int(request.form.get('sure_dakika', 0))
            toplam_dakika = (sure_saat * 60) + sure_dakika
            
            is_gunlugu = IsGunlugu(
                is_kodu=is_kodu,
                tarih=datetime.strptime(request.form['tarih'], '%Y-%m-%d').date(),
                musteri_id=musteri.id,
                proje=request.form.get('proje', ''),
                aktivite_turu=request.form['aktivite_turu'],
                aciklama=request.form['aciklama'],
                sorumlu_kisi=request.form.get('sorumlu_kisi', ''),
                sure_dakika=toplam_dakika,
                etiketler=request.form.get('etiketler', ''),
                durum='Bekliyor'
            )
            db.session.add(is_gunlugu)
            db.session.commit()
            logger.info(f"İş başarıyla eklendi - Kod: {is_gunlugu.is_kodu}")
            flash(f'İş günlüğü başarıyla eklendi! İş Kodu: {is_gunlugu.is_kodu}', 'success')
            
            # Eğer müşteri_id parametresi varsa müşteri detaya dön
            musteri_id_param = request.args.get('musteri_id') or request.form.get('musteri_id')
            if musteri_id_param:
                return redirect(url_for('musteri_detay', musteri_id=musteri_id_param))
            return redirect(url_for('is_gunlugu'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"İş ekleme hatası: {str(e)}", exc_info=True)
            flash(f'Hata: {str(e)}', 'error')

    return render_template('is_ekle.html', musteriler=musteriler)

# Teslimatlar
@app.route('/teslimatlar')
def teslimatlar():
    teslimatlar = Teslimat.query.all()
    return render_template('teslimatlar.html', teslimatlar=teslimatlar)

@app.route('/teslimat_ekle', methods=['GET', 'POST'])
@app.route('/teslimat_ekle/<int:musteri_id>', methods=['GET', 'POST'])
def teslimat_ekle(musteri_id=None):
    musteriler = Musteri.query.all()
    if request.method == 'POST':
        try:
            musteri = Musteri.query.get(int(request.form['musteri_id']))
            if not musteri:
                flash('Müşteri bulunamadı!', 'error')
                return redirect(url_for('teslimat_ekle'))
            
            # Otomatik teslimat kodu oluştur
            teslimat_kodu = generate_teslimat_kodu(musteri)
            logger.info(f"Oluşturulan teslimat kodu: {teslimat_kodu}")
            
            teslimat = Teslimat(
                teslimat_kodu=teslimat_kodu,
                musteri_id=musteri.id,
                aktivite_turu=request.form.get('aktivite_turu', ''),
                proje=request.form.get('proje', ''),
                teslim_turu=request.form['teslim_turu'],
                baslik=request.form['baslik'],
                sorumlu_kisi=request.form['sorumlu_kisi'],
                olusturma_tarihi=datetime.strptime(request.form['olusturma_tarihi'], '%Y-%m-%d').date(),
                teslim_tarihi=datetime.strptime(request.form['teslim_tarihi'], '%Y-%m-%d').date(),
                durum=request.form['durum'],
                aciklama=request.form['aciklama']
            )
            db.session.add(teslimat)
            db.session.commit()
            logger.info(f"Teslimat başarıyla eklendi - Kod: {teslimat.teslimat_kodu}")
            flash(f'Teslimat başarıyla eklendi! Teslimat Kodu: {teslimat.teslimat_kodu}')
            if musteri_id:
                return redirect(url_for('musteri_detay', musteri_id=musteri_id))
            return redirect(url_for('teslimatlar'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Teslimat ekleme hatası: {str(e)}", exc_info=True)
            flash(f'Hata: {str(e)}', 'error')

    return render_template('teslimat_ekle.html', musteriler=musteriler, secili_musteri_id=musteri_id)

# Sosyal medya
@app.route('/sosyal_medya')
def sosyal_medya():
    sosyal_medyalar = SosyalMedya.query.all()
    return render_template('sosyal_medya.html', sosyal_medyalar=sosyal_medyalar)

@app.route('/sosyal_medya_ekle', methods=['GET', 'POST'])
@app.route('/sosyal_medya_ekle/<int:musteri_id>', methods=['GET', 'POST'])
def sosyal_medya_ekle(musteri_id=None):
    musteriler = Musteri.query.all()
    isler = IsGunlugu.query.filter_by(musteri_id=musteri_id).all() if musteri_id else []
    
    if request.method == 'POST':
        is_gunlugu_id = int(request.form['is_gunlugu_id']) if request.form.get('is_gunlugu_id') else None
        
        sosyal = SosyalMedya(
            tarih=datetime.strptime(request.form['tarih'], '%Y-%m-%d').date(),
            musteri_id=int(request.form['musteri_id']),
            is_gunlugu_id=is_gunlugu_id,
            platform=request.form['platform'],
            icerik_basligi=request.form['icerik_basligi'],
            gonderi_turu=request.form['gonderi_turu'],
            etkileşim=int(request.form.get('etkilesim', 0)),
            goruntulenme=int(request.form.get('goruntulenme', 0)),
            begeni=int(request.form.get('begeni', 0)),
            yorum=int(request.form.get('yorum', 0)),
            paylasim=int(request.form.get('paylasim', 0)),
            durum=request.form['durum']
        )
        db.session.add(sosyal)
        db.session.commit()
        
        # İş kodu ile flash mesajı
        if is_gunlugu_id:
            is_gunlugu = IsGunlugu.query.get(is_gunlugu_id)
            flash(f'Sosyal medya kaydı başarıyla eklendi! ({is_gunlugu.is_kodu if is_gunlugu else ""})', 'success')
        else:
            flash('Sosyal medya kaydı başarıyla eklendi!', 'success')
        
        if musteri_id:
            return redirect(url_for('musteri_detay', musteri_id=musteri_id))
        return redirect(url_for('sosyal_medya'))

    return render_template('sosyal_medya_ekle.html', musteriler=musteriler, isler=isler, secili_musteri_id=musteri_id)

# API endpoint - İş detayı getir
@app.route('/api/is_detay/<int:is_id>')
def api_is_detay(is_id):
    """İş detayı JSON olarak döndür"""
    is_gunlugu = IsGunlugu.query.get_or_404(is_id)
    
    # Revizyonları çek
    revizyonlar = Revizyon.query.filter_by(is_gunlugu_id=is_id).order_by(Revizyon.revizyon_numarasi).all()
    
    # Teslimatı çek
    teslimat = Teslimat.query.filter_by(is_gunlugu_id=is_id).first()
    
    result = {
        'is_kodu': is_gunlugu.is_kodu,
        'tarih': is_gunlugu.tarih.strftime('%d.%m.%Y'),
        'proje': is_gunlugu.proje or '-',
        'aktivite_turu': is_gunlugu.aktivite_turu or '-',
        'aciklama': is_gunlugu.aciklama or '-',
        'sorumlu_kisi': is_gunlugu.sorumlu_kisi or '-',
        'sure_saat': (is_gunlugu.sure_dakika // 60) if is_gunlugu.sure_dakika else 0,
        'sure_dakika': (is_gunlugu.sure_dakika % 60) if is_gunlugu.sure_dakika else 0,
        'etiketler': is_gunlugu.etiketler or '-',
        'durum': is_gunlugu.durum or 'Bekliyor',
        'revizyon_sayisi': is_gunlugu.revizyon_sayisi or 0,
        'revizyonlar': [{
            'baslik': rev.baslik,
            'tarih': rev.tarih.strftime('%d.%m.%Y'),
            'talep_eden': rev.revize_talep_eden,
            'konu': rev.revize_konusu,
            'durum': rev.durum
        } for rev in revizyonlar],
        'teslimat': {
            'var': teslimat is not None,
            'teslim_turu': teslimat.teslim_turu if teslimat else None,
            'durum': teslimat.durum if teslimat else None,
            'teslim_tarihi': teslimat.teslim_tarihi.strftime('%d.%m.%Y') if teslimat and teslimat.teslim_tarihi else None,
            'platform': teslimat.platform if teslimat else None,
            'gonderi_turu': teslimat.gonderi_turu if teslimat else None,
            'etkileşim': teslimat.etkileşim if teslimat else 0,
            'goruntulenme': teslimat.goruntulenme if teslimat else 0,
            'begeni': teslimat.begeni if teslimat else 0,
            'yorum': teslimat.yorum if teslimat else 0,
            'paylasim': teslimat.paylasim if teslimat else 0
        } if teslimat else None
    }
    
    return jsonify(result)

# API endpoint - Müşteriye göre teslimatları getir
@app.route('/api/teslimatlar/<int:musteri_id>')
def api_teslimatlar(musteri_id):
    teslimatlar = Teslimat.query.filter_by(musteri_id=musteri_id).all()
    result = []
    for teslimat in teslimatlar:
        result.append({
            'id': teslimat.id,
            'baslik': teslimat.baslik,
            'durum': teslimat.durum
        })
    return jsonify(result)

# API endpoint - İş tipi dağılımı filtreleme
@app.route('/api/is_tipi_dagilimi')
def api_is_tipi_dagilimi():
    from src.utils.statistics import get_is_tipi_dagilimi
    from datetime import datetime, timedelta
    
    filtre = request.args.get('filtre', 'ay')
    today = datetime.now().date()
    
    if filtre == 'ay':
        # Bu ayın ilk günü
        start_date = datetime(today.year, today.month, 1).date()
        end_date = None
    elif filtre == 'yil':
        # Bu yılın ilk günü
        start_date = datetime(today.year, 1, 1).date()
        end_date = None
    else:  # 'tumu'
        start_date = None
        end_date = None
    
    data = get_is_tipi_dagilimi(db, start_date, end_date)
    return jsonify(data)

# İş onay/red/revize route'ları
@app.route('/is_onaya_gonder/<int:is_id>', methods=['POST'])
def is_onaya_gonder(is_id):
    """İşi onaya gönder (revizyonlardan)"""
    try:
        is_gunlugu = IsGunlugu.query.get_or_404(is_id)
        is_gunlugu.durum = 'Onayda'
        db.session.commit()
        flash('İş onaya gönderildi!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"İş onaya gönder hatası: {str(e)}", exc_info=True)
        flash(f'Hata: {str(e)}', 'error')
    
    return redirect(url_for('musteri_detay', musteri_id=is_gunlugu.musteri_id))

@app.route('/is_onay/<int:is_id>', methods=['POST'])
def is_onay(is_id):
    """İşi onayla ve otomatik teslimat oluştur"""
    try:
        is_gunlugu = IsGunlugu.query.get_or_404(is_id)
        musteri = Musteri.query.get(is_gunlugu.musteri_id)
        
        # İş durumunu onaylandı yap
        is_gunlugu.durum = 'Onaylandı'
        
        # Sadece SON revizyonu "Onaylandı" yap
        son_revizyon = Revizyon.query.filter_by(is_gunlugu_id=is_id).order_by(Revizyon.revizyon_numarasi.desc()).first()
        if son_revizyon:
            son_revizyon.durum = 'Onaylandı'
        
        # Otomatik teslimat oluştur (İş Kodu ile takip edilecek)
        teslimat = Teslimat(
            is_gunlugu_id=is_id,
            musteri_id=is_gunlugu.musteri_id,
            baslik=is_gunlugu.aciklama or is_gunlugu.proje,
            proje=is_gunlugu.proje,
            sorumlu_kisi=is_gunlugu.sorumlu_kisi,
            olusturma_tarihi=is_gunlugu.tarih,
            teslim_tarihi=date.today(),
            durum='Hazırlanıyor',
            aciklama=f"İş Kodu: {is_gunlugu.is_kodu} - Otomatik oluşturuldu"
        )
        db.session.add(teslimat)
        db.session.commit()
        
        flash(f'{is_gunlugu.is_kodu} onaylandı ve teslimat oluşturuldu!', 'success')
        return redirect(url_for('teslimat_duzenle', teslimat_id=teslimat.id))
    except Exception as e:
        db.session.rollback()
        logger.error(f"İş onay hatası: {str(e)}", exc_info=True)
        flash(f'Hata: {str(e)}', 'error')
        return redirect(url_for('musteri_detay', musteri_id=is_gunlugu.musteri_id))

@app.route('/is_red/<int:is_id>', methods=['POST'])
def is_red(is_id):
    """İşi reddet"""
    try:
        is_gunlugu = IsGunlugu.query.get_or_404(is_id)
        is_gunlugu.durum = 'Reddedildi'
        
        # Sadece SON revizyonu "Reddedildi" yap
        son_revizyon = Revizyon.query.filter_by(is_gunlugu_id=is_id).order_by(Revizyon.revizyon_numarasi.desc()).first()
        if son_revizyon:
            son_revizyon.durum = 'Reddedildi'
        
        db.session.commit()
        flash(f'{is_gunlugu.is_kodu} reddedildi!', 'danger')
    except Exception as e:
        db.session.rollback()
        logger.error(f"İş red hatası: {str(e)}", exc_info=True)
        flash(f'Hata: {str(e)}', 'error')
    
    return redirect(url_for('musteri_detay', musteri_id=is_gunlugu.musteri_id))

@app.route('/is_tekrar_revize/<int:is_id>', methods=['POST'])
def is_tekrar_revize(is_id):
    """İşi tekrar revizeye gönder"""
    try:
        is_gunlugu = IsGunlugu.query.get_or_404(is_id)
        is_gunlugu.durum = 'Revizede'
        
        # SON revizyonun durumunu "Tekrar Revizeye Gitti" yap
        son_revizyon = Revizyon.query.filter_by(is_gunlugu_id=is_id).order_by(Revizyon.revizyon_numarasi.desc()).first()
        if son_revizyon:
            son_revizyon.durum = 'Tekrar Revizeye Gitti'
        
        db.session.commit()
        
        # Yeni revizyon numarasını JSON olarak döndür (modal için)
        return jsonify({
            'success': True,
            'is_id': is_id,
            'is_kodu': is_gunlugu.is_kodu,
            'revizyon_numarasi': (is_gunlugu.revizyon_sayisi or 0) + 1,
            'message': f'{is_gunlugu.is_kodu} tekrar revizeye gönderildi!'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"İş tekrar revize hatası: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# Revizyon ekleme
@app.route('/revizyon_ekle', methods=['GET', 'POST'])
@app.route('/revizyon_ekle/<int:musteri_id>', methods=['GET', 'POST'])
def revizyon_ekle(musteri_id=None):
    if request.method == 'POST':
        try:
            logger.info(f"Revizyon ekleme işlemi başladı - Musteri ID: {request.form.get('musteri_id')}")
            logger.info(f"Form verileri: {dict(request.form)}")
            
            is_gunlugu_id = int(request.form['is_gunlugu_id']) if request.form.get('is_gunlugu_id') else None
            
            # Önceki revizyonun durumunu "Tekrar Revize Geldi" yap
            revizyon_numarasi = 1
            baslik = "Revizyon 1"
            
            if is_gunlugu_id:
                # Önceki revizyonu bul ve durumunu güncelle
                onceki_revizyon = Revizyon.query.filter_by(is_gunlugu_id=is_gunlugu_id)\
                    .order_by(Revizyon.revizyon_numarasi.desc()).first()
                if onceki_revizyon:
                    onceki_revizyon.durum = 'Tekrar Revize Geldi'
                
                # İş günlüğü durumunu ve revizyon sayısını güncelle
                is_gunlugu = IsGunlugu.query.get(is_gunlugu_id)
                if is_gunlugu:
                    # İş durumunu Revizede yap
                    is_gunlugu.durum = 'Revizede'
                    # Revizyon sayısını artır
                    is_gunlugu.revizyon_sayisi = (is_gunlugu.revizyon_sayisi or 0) + 1
                    revizyon_numarasi = is_gunlugu.revizyon_sayisi
                    baslik = f"Revizyon {revizyon_numarasi}"
                    db.session.commit()
            
            revizyon = Revizyon(
                tarih=datetime.strptime(request.form['tarih'], '%Y-%m-%d').date(),
                musteri_id=int(request.form['musteri_id']),
                is_gunlugu_id=is_gunlugu_id,
                revizyon_numarasi=revizyon_numarasi,
                baslik=baslik,
                revize_talep_eden=request.form['revize_talep_eden'],
                revize_konusu=request.form['revize_konusu'],
                durum='Bekliyor'
            )
            
            logger.info(f"Revizyon objesi oluşturuldu: Musteri={revizyon.musteri_id}, Is={revizyon.is_gunlugu_id}, Baslik={baslik}")
            
            db.session.add(revizyon)
            db.session.commit()
            
            logger.info(f"Revizyon başarıyla eklendi - ID: {revizyon.id}")
            flash(f'{baslik} başarıyla eklendi!')
            
            if musteri_id:
                return redirect(url_for('musteri_detay', musteri_id=musteri_id))
            return redirect(url_for('musteriler'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Revizyon ekleme hatası: {str(e)}", exc_info=True)
            flash(f'Hata: {str(e)}', 'error')

    musteriler = Musteri.query.all()
    isler = IsGunlugu.query.all()
    return render_template('revizyon_ekle.html',
                         musteriler=musteriler,
                         isler=isler,
                         secili_musteri_id=musteri_id)

# İş Düzenleme Route'u
@app.route('/is_duzenle/<int:is_id>', methods=['GET', 'POST'])
def is_duzenle(is_id):
    """İş günlüğü düzenleme - cascade güncelleme"""
    is_gunlugu = IsGunlugu.query.get_or_404(is_id)
    
    if request.method == 'POST':
        try:
            # Saat ve dakikayı toplam dakikaya çevir
            sure_saat = int(request.form.get('sure_saat', 0))
            sure_dakika_input = int(request.form.get('sure_dakika_input', 0))
            toplam_dakika = (sure_saat * 60) + sure_dakika_input
            
            # İş günlüğünü güncelle
            is_gunlugu.tarih = datetime.strptime(request.form['tarih'], '%Y-%m-%d').date()
            is_gunlugu.proje = request.form.get('proje', '')
            is_gunlugu.aktivite_turu = request.form['aktivite_turu']
            is_gunlugu.aciklama = request.form['aciklama']
            is_gunlugu.sorumlu_kisi = request.form.get('sorumlu_kisi', '')
            is_gunlugu.sure_dakika = toplam_dakika
            is_gunlugu.etiketler = request.form.get('etiketler', '')
            
            # Cascade: Revizyonları güncelle
            revizyonlar = Revizyon.query.filter_by(is_gunlugu_id=is_id).all()
            for rev in revizyonlar:
                rev.musteri_id = is_gunlugu.musteri_id
                rev.tarih = is_gunlugu.tarih
            
            # Cascade: Teslimatı güncelle
            teslimat = Teslimat.query.filter_by(is_gunlugu_id=is_id).first()
            if teslimat:
                teslimat.baslik = is_gunlugu.aciklama or is_gunlugu.proje
                teslimat.proje = is_gunlugu.proje
                teslimat.sorumlu_kisi = is_gunlugu.sorumlu_kisi
                teslimat.olusturma_tarihi = is_gunlugu.tarih
            
            db.session.commit()
            flash(f'{is_gunlugu.is_kodu} başarıyla güncellendi!', 'success')
            return redirect(url_for('musteri_detay', musteri_id=is_gunlugu.musteri_id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"İş düzenleme hatası: {str(e)}", exc_info=True)
            flash(f'Hata: {str(e)}', 'error')
    
    musteriler = Musteri.query.all()
    return render_template('is_duzenle.html', is_gunlugu=is_gunlugu, musteriler=musteriler)

# Teslimat Düzenleme
@app.route('/teslimat_duzenle/<int:teslimat_id>', methods=['GET', 'POST'])
def teslimat_duzenle(teslimat_id):
    """Teslimat düzenleme - sosyal medya entegrasyonu"""
    teslimat = Teslimat.query.get_or_404(teslimat_id)
    musteriler = Musteri.query.all()
    
    if request.method == 'POST':
        try:
            # Temel bilgileri güncelle
            teslimat.teslim_turu = request.form['teslim_turu']
            teslimat.baslik = request.form['baslik']
            teslimat.proje = request.form.get('proje', '')
            teslimat.sorumlu_kisi = request.form['sorumlu_kisi']
            teslimat.teslim_tarihi = datetime.strptime(request.form['teslim_tarihi'], '%Y-%m-%d').date()
            teslimat.durum = request.form['durum']
            teslimat.aciklama = request.form.get('aciklama', '')
            
            # Sosyal Medya ise metrik alanlarını güncelle
            if teslimat.teslim_turu == 'Sosyal Medya':
                teslimat.platform = request.form.get('platform', '')
                teslimat.gonderi_turu = request.form.get('gonderi_turu', '')
                teslimat.etkileşim = int(request.form.get('etkilesim', 0) or 0)
                teslimat.goruntulenme = int(request.form.get('goruntulenme', 0) or 0)
                teslimat.begeni = int(request.form.get('begeni', 0) or 0)
                teslimat.yorum = int(request.form.get('yorum', 0) or 0)
                teslimat.paylasim = int(request.form.get('paylasim', 0) or 0)
            else:
                # Sosyal Medya değilse metrikleri sıfırla
                teslimat.platform = None
                teslimat.gonderi_turu = None
                teslimat.etkileşim = None
                teslimat.goruntulenme = None
                teslimat.begeni = None
                teslimat.yorum = None
                teslimat.paylasim = None
            
            db.session.commit()
            # İş kodunu bul
            is_gunlugu = IsGunlugu.query.get(teslimat.is_gunlugu_id)
            is_kodu = is_gunlugu.is_kodu if is_gunlugu else 'Teslimat'
            flash(f'{is_kodu} teslimatı başarıyla güncellendi!', 'success')
            return redirect(url_for('musteri_detay', musteri_id=teslimat.musteri_id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Teslimat düzenleme hatası: {str(e)}", exc_info=True)
            flash(f'Hata: {str(e)}', 'error')
    
    # İş günlüğünü de gönder (iş kodu göstermek için)
    isler = IsGunlugu.query.filter_by(musteri_id=teslimat.musteri_id).all()
    return render_template('teslimat_duzenle.html', teslimat=teslimat, musteriler=musteriler, isler=isler)

# Teslimat Silme
@app.route('/teslimat_sil/<int:teslimat_id>', methods=['POST'])
def teslimat_sil(teslimat_id):
    """Teslimat silme"""
    try:
        teslimat = Teslimat.query.get_or_404(teslimat_id)
        musteri_id = teslimat.musteri_id
        
        # İş kodunu bul
        is_gunlugu = IsGunlugu.query.get(teslimat.is_gunlugu_id) if teslimat.is_gunlugu_id else None
        is_kodu = is_gunlugu.is_kodu if is_gunlugu else 'Teslimat'
        
        db.session.delete(teslimat)
        db.session.commit()
        
        flash(f'{is_kodu} teslimatı silindi!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Teslimat silme hatası: {str(e)}", exc_info=True)
        flash(f'Hata: {str(e)}', 'error')
    
    return redirect(url_for('musteri_detay', musteri_id=musteri_id))

# Excel import/export
@app.route('/excel_import', methods=['GET', 'POST'])
def excel_import():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Excel'den veri oku ve veritabanına aktar
            df = pd.read_excel(filepath)

            # Müşterileri içe aktar
            if 'Müşteri Adı' in df.columns:
                for _, row in df.iterrows():
                    musteri = Musteri(
                        ad=row['Müşteri Adı'],
                        sektor=row.get('Sektör', ''),
                        aylik_ucret=row.get('Aylık Ücret (TL)', 0),
                        ilgil_kisi=row.get('İlgili Kişi', ''),
                        telefon=row.get('Telefon', ''),
                        email=row.get('E-posta', ''),
                        notlar=row.get('Notlar', '')
                    )
                    db.session.add(musteri)

            db.session.commit()
            flash('Excel verisi başarıyla içe aktarıldı!')
            return redirect(url_for('index'))

    return render_template('excel_import.html')

# CRM - Arama Kayıtları
@app.route('/aramalar')
def aramalar():
    aramalar = Arama.query.order_by(Arama.tarih.desc()).all()
    # Geri dönüş gereken aramalar
    from datetime import date
    today = date.today()
    geri_donus_gereken = Arama.query.filter(
        Arama.geri_donus_tarihi.isnot(None),
        Arama.geri_donus_tarihi <= today,
        Arama.durum == 'Bekliyor'
    ).count()
    return render_template('aramalar.html', 
                         aramalar=aramalar,
                         geri_donus_gereken=geri_donus_gereken)

@app.route('/arama_ekle', methods=['GET', 'POST'])
@app.route('/arama_ekle/<int:musteri_id>', methods=['GET', 'POST'])
def arama_ekle(musteri_id=None):
    musteriler = Musteri.query.all()
    if request.method == 'POST':
        try:
            logger.info(f"Arama ekleme başladı - Müşteri: {request.form.get('musteri_id')}")
            
            geri_donus_str = request.form.get('geri_donus_tarihi')
            geri_donus_tarihi = None
            if geri_donus_str:
                geri_donus_tarihi = datetime.strptime(geri_donus_str, '%Y-%m-%d').date()
            
            arama = Arama(
                tarih=datetime.strptime(request.form['tarih'], '%Y-%m-%d').date(),
                musteri_id=int(request.form['musteri_id']),
                arayan_aranan=request.form['arayan_aranan'],
                konu=request.form['konu'],
                sonuc=request.form['sonuc'],
                sorumlu_kisi=request.form.get('sorumlu_kisi', ''),
                notlar=request.form.get('notlar', ''),
                geri_donus_tarihi=geri_donus_tarihi,
                durum='Bekliyor' if geri_donus_tarihi else 'Tamamlandı'
            )
            
            db.session.add(arama)
            db.session.commit()
            logger.info(f"Arama başarıyla eklendi - ID: {arama.id}")
            flash('Arama kaydı başarıyla eklendi!')
            
            if musteri_id:
                return redirect(url_for('musteri_detay', musteri_id=musteri_id))
            return redirect(url_for('aramalar'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Arama ekleme hatası: {str(e)}", exc_info=True)
            flash(f'Hata: {str(e)}', 'error')
    
    return render_template('arama_ekle.html', 
                         musteriler=musteriler,
                         secili_musteri_id=musteri_id)

@app.route('/arama_duzenle/<int:arama_id>', methods=['GET', 'POST'])
def arama_duzenle(arama_id):
    arama = Arama.query.get_or_404(arama_id)
    musteriler = Musteri.query.all()
    
    if request.method == 'POST':
        try:
            arama.tarih = datetime.strptime(request.form['tarih'], '%Y-%m-%d').date()
            arama.musteri_id = int(request.form['musteri_id'])
            arama.arayan_aranan = request.form['arayan_aranan']
            arama.konu = request.form['konu']
            arama.sonuc = request.form['sonuc']
            arama.sorumlu_kisi = request.form.get('sorumlu_kisi', '')
            arama.notlar = request.form.get('notlar', '')
            
            geri_donus_str = request.form.get('geri_donus_tarihi')
            if geri_donus_str:
                arama.geri_donus_tarihi = datetime.strptime(geri_donus_str, '%Y-%m-%d').date()
            else:
                arama.geri_donus_tarihi = None
            
            arama.durum = request.form.get('durum', 'Bekliyor')
            
            db.session.commit()
            flash('Arama kaydı güncellendi!')
            return redirect(url_for('aramalar'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Arama güncelleme hatası: {str(e)}", exc_info=True)
            flash(f'Hata: {str(e)}', 'error')
    
    return render_template('arama_ekle.html', 
                         arama=arama,
                         musteriler=musteriler,
                         secili_musteri_id=arama.musteri_id)

@app.route('/arama_sil/<int:arama_id>', methods=['POST'])
def arama_sil(arama_id):
    try:
        arama = Arama.query.get_or_404(arama_id)
        db.session.delete(arama)
        db.session.commit()
        flash('Arama kaydı silindi!')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Arama silme hatası: {str(e)}", exc_info=True)
        flash(f'Hata: {str(e)}', 'error')
    return redirect(url_for('aramalar'))

# Müşteri raporu Word indirme
@app.route('/musteri/<int:musteri_id>/rapor')
def musteri_rapor_indir(musteri_id):
    try:
        from src.utils.report_generator import generate_musteri_raporu
        from datetime import datetime, timedelta
        from flask import send_file
        import os
        
        musteri = Musteri.query.get_or_404(musteri_id)
        
        # Filtre parametresi
        filtre = request.args.get('filtre', 'ay')
        today = datetime.now().date()
        
        # Tarih aralığını belirle
        if filtre == 'ay':
            start_date = datetime(today.year, today.month, 1).date()
            end_date = None
        elif filtre == 'yil':
            start_date = datetime(today.year, 1, 1).date()
            end_date = None
        elif filtre == '6ay':
            start_date = today - timedelta(days=180)
            end_date = None
        else:  # 'tumu'
            start_date = None
            end_date = None
        
        # Upload klasörünün var olduğundan emin ol
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Rapor oluştur
        doc = generate_musteri_raporu(db, musteri, start_date, end_date)
        
        # Dosya adı oluştur (Türkçe karakterleri temizle)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = musteri.ad.replace(' ', '_').replace('ş', 's').replace('ğ', 'g').replace('ü', 'u').replace('ö', 'o').replace('ç', 'c').replace('ı', 'i')
        filename = f"{safe_name}_{timestamp}_rapor.docx"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Kaydet
        doc.save(filepath)
        
        # İndir (Flask versiyonuna göre uyumlu)
        try:
            # Flask 2.0+ için download_name
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        except TypeError:
            # Flask 1.x için attachment_filename
            return send_file(
                filepath,
                as_attachment=True,
                attachment_filename=filename,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
    except ImportError as e:
        logger.error(f"Import hatası: {str(e)}", exc_info=True)
        flash(f'Rapor modülü yüklenemedi. Lütfen python-docx kütüphanesinin kurulu olduğundan emin olun: {str(e)}', 'error')
        return redirect(url_for('musteri_detay', musteri_id=musteri_id))
    except Exception as e:
        logger.error(f"Rapor oluşturma hatası: {str(e)}", exc_info=True)
        flash(f'Rapor oluşturulurken hata: {str(e)}', 'error')
        return redirect(url_for('musteri_detay', musteri_id=musteri_id))

@app.route('/excel_export')
def excel_export():
    # Tüm verileri Excel'e export et
    with pd.ExcelWriter('ajans_raporu.xlsx', engine='openpyxl') as writer:
        # Müşteriler
        musteriler = pd.read_sql('SELECT * FROM musteri', db.engine)
        musteriler.to_excel(writer, sheet_name='Müşteriler', index=False)

        # İş günlüğü
        isler = pd.read_sql('SELECT * FROM is_gunlugu', db.engine)
        isler.to_excel(writer, sheet_name='İş Günlüğü', index=False)

        # Teslimatlar
        teslimatlar = pd.read_sql('SELECT * FROM teslimat', db.engine)
        teslimatlar.to_excel(writer, sheet_name='Teslimatlar', index=False)

        # Sosyal medya
        sosyal = pd.read_sql('SELECT * FROM sosyal_medya', db.engine)
        sosyal.to_excel(writer, sheet_name='Sosyal Medya', index=False)

    flash('Veriler Excel dosyasına export edildi!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
    app.run(debug=True, host='0.0.0.0', port=5000)