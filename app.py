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
    tarih = db.Column(db.Date, nullable=False)
    musteri_id = db.Column(db.Integer, db.ForeignKey('musteri.id'))
    proje = db.Column(db.String(100))
    aktivite_turu = db.Column(db.String(50))
    aciklama = db.Column(db.Text)
    sorumlu_kisi = db.Column(db.String(100))
    sure_dakika = db.Column(db.Integer)
    etiketler = db.Column(db.String(200))

class Teslimat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teslimat_kodu = db.Column(db.String(30), unique=True)  # TSL-MST001-001, TSL-MST001-002, etc.
    musteri_id = db.Column(db.Integer, db.ForeignKey('musteri.id'))
    aktivite_turu = db.Column(db.String(50))
    proje = db.Column(db.String(100))
    teslim_turu = db.Column(db.String(50))
    baslik = db.Column(db.String(100))
    sorumlu_kisi = db.Column(db.String(100))
    olusturma_tarihi = db.Column(db.Date)
    teslim_tarihi = db.Column(db.Date)
    durum = db.Column(db.String(20))
    aciklama = db.Column(db.Text)

class SosyalMedya(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.Date, nullable=False)
    musteri_id = db.Column(db.Integer, db.ForeignKey('musteri.id'))
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
    teslimat_id = db.Column(db.Integer, db.ForeignKey('teslimat.id'))
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
    musteri = Musteri.query.get_or_404(musteri_id)
    teslimatlar = Teslimat.query.filter_by(musteri_id=musteri_id).all()
    sosyal_medyalar = SosyalMedya.query.filter_by(musteri_id=musteri_id).all()
    revizyonlar = Revizyon.query.filter_by(musteri_id=musteri_id).all()
    return render_template('musteri_detay.html',
                         musteri=musteri,
                         teslimatlar=teslimatlar,
                         sosyal_medyalar=sosyal_medyalar,
                         revizyonlar=revizyonlar)

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
        is_gunlugu = IsGunlugu(
            tarih=datetime.strptime(request.form['tarih'], '%Y-%m-%d').date(),
            musteri_id=int(request.form['musteri_id']),
            proje=request.form['proje'],
            aktivite_turu=request.form['aktivite_turu'],
            aciklama=request.form['aciklama'],
            sorumlu_kisi=request.form['sorumlu_kisi'],
            sure_dakika=int(request.form['sure_dakika']),
            etiketler=request.form['etiketler']
        )
        db.session.add(is_gunlugu)
        db.session.commit()
        flash('İş günlüğü başarıyla eklendi!')
        return redirect(url_for('is_gunlugu'))

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
    if request.method == 'POST':
        sosyal = SosyalMedya(
            tarih=datetime.strptime(request.form['tarih'], '%Y-%m-%d').date(),
            musteri_id=int(request.form['musteri_id']),
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
        flash('Sosyal medya kaydı başarıyla eklendi!')
        if musteri_id:
            return redirect(url_for('musteri_detay', musteri_id=musteri_id))
        return redirect(url_for('sosyal_medya'))

    return render_template('sosyal_medya_ekle.html', musteriler=musteriler, secili_musteri_id=musteri_id)

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

# Revizyon ekleme
@app.route('/revizyon_ekle', methods=['GET', 'POST'])
@app.route('/revizyon_ekle/<int:musteri_id>', methods=['GET', 'POST'])
def revizyon_ekle(musteri_id=None):
    if request.method == 'POST':
        try:
            logger.info(f"Revizyon ekleme işlemi başladı - Musteri ID: {request.form.get('musteri_id')}")
            logger.info(f"Form verileri: {dict(request.form)}")
            
            revizyon = Revizyon(
                tarih=datetime.strptime(request.form['tarih'], '%Y-%m-%d').date(),
                musteri_id=int(request.form['musteri_id']),
                teslimat_id=int(request.form['teslimat_id']) if request.form.get('teslimat_id') else None,
                revize_talep_eden=request.form['revize_talep_eden'],
                revize_konusu=request.form['revize_konusu'],
                durum='Bekliyor'
            )
            
            logger.info(f"Revizyon objesi oluşturuldu: Musteri={revizyon.musteri_id}, Teslimat={revizyon.teslimat_id}")
            
            db.session.add(revizyon)
            db.session.commit()
            
            logger.info(f"Revizyon başarıyla eklendi - ID: {revizyon.id}")
            flash('Revizyon başarıyla eklendi!')
            
            if musteri_id:
                return redirect(url_for('musteri_detay', musteri_id=musteri_id))
            return redirect(url_for('musteriler'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Revizyon ekleme hatası: {str(e)}", exc_info=True)
            flash(f'Hata: {str(e)}', 'error')

    musteriler = Musteri.query.all()
    teslimatlar = Teslimat.query.all()
    return render_template('revizyon_ekle.html',
                         musteriler=musteriler,
                         teslimatlar=teslimatlar,
                         secili_musteri_id=musteri_id)

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