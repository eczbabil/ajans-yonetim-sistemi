from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from src.models import Musteri, Teslimat, SosyalMedya, Revizyon
from src.utils.database import db

musteri_bp = Blueprint('musteri', __name__)

@musteri_bp.route('/musteriler')
def musteriler():
    """Müşteri listesi"""
    musteriler = Musteri.query.all()
    return render_template('musteriler.html', musteriler=musteriler)

@musteri_bp.route('/musteri_detay/<int:musteri_id>')
def musteri_detay(musteri_id):
    """Müşteri detay sayfası - dashboard istatistikleri ile"""
    from src.models import IsGunlugu, Arama
    from sqlalchemy import func
    
    musteri = Musteri.query.get_or_404(musteri_id)
    
    # İş günlüğü kayıtları
    isler = IsGunlugu.query.filter_by(musteri_id=musteri_id).order_by(IsGunlugu.tarih.desc()).all()
    
    # Teslimatlar
    teslimatlar = Teslimat.query.filter_by(musteri_id=musteri_id).all()
    
    # Revizyonlar (iş kodu ile birlikte)
    revizyonlar = Revizyon.query.filter_by(musteri_id=musteri_id).order_by(Revizyon.tarih.desc()).all()
    
    # Aramalar
    try:
        aramalar = Arama.query.filter_by(musteri_id=musteri_id).order_by(Arama.tarih.desc()).limit(10).all()
    except:
        aramalar = []
    
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
    
    # Onayda bekleyen işler
    onayda_bekleyenler = [is_item for is_item in isler if is_item.durum == 'Onayda']
    
    return render_template('musteri_detay.html',
                         musteri=musteri,
                         isler=isler,
                         teslimatlar=teslimatlar,
                         revizyonlar=revizyonlar,
                         aramalar=aramalar,
                         onayda_bekleyenler=onayda_bekleyenler,
                         # Dashboard istatistikleri
                         toplam_saat=toplam_saat,
                         onaylanan_teslimatlar=onaylanan_teslimatlar,
                         devam_eden_teslimatlar=devam_eden_teslimatlar,
                         toplam_is=toplam_is,
                         toplam_teslimat=toplam_teslimat,
                         sosyal_medya_teslimat=sosyal_medya_teslimat)

@musteri_bp.route('/musteri_ekle', methods=['GET', 'POST'])
def musteri_ekle():
    """Müşteri ekleme"""
    if request.method == 'POST':
        try:
            musteri = Musteri(
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
            flash('Müşteri başarıyla eklendi!', 'success')
            return redirect(url_for('musteri.musteriler'))
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'error')
    
    return render_template('musteri_ekle.html')
