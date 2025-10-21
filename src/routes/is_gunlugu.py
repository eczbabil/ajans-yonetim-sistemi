from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from src.models import IsGunlugu, Musteri, Revizyon, Teslimat
from src.utils.database import db

is_gunlugu_bp = Blueprint('is_gunlugu', __name__)

def generate_teslimat_kodu(musteri):
    """Teslimat kodu oluştur: TSL-MST001-001"""
    from src.models import Teslimat
    
    # Müşteri için son teslimat kodunu bul
    son_teslimat = Teslimat.query.filter_by(musteri_id=musteri.id)\
        .order_by(Teslimat.id.desc()).first()
    
    if son_teslimat and son_teslimat.teslimat_kodu:
        # Son teslimat kodundan numarayı çıkar: TSL-MST001-001 -> 001
        parts = son_teslimat.teslimat_kodu.split('-')
        if len(parts) == 3:
            son_numara = int(parts[2])
            yeni_numara = son_numara + 1
        else:
            yeni_numara = 1
    else:
        yeni_numara = 1
    
    # TSL-MST001-001 formatında kod oluştur
    musteri_kodu_sayi = musteri.musteri_kodu.replace('MST-', '').replace('MST', '')
    teslimat_kodu = f"TSL-MST{musteri_kodu_sayi}-{yeni_numara:03d}"
    
    return teslimat_kodu

@is_gunlugu_bp.route('/is_gunlugu')
def is_gunlugu():
    """İş günlüğü listesi"""
    isler = IsGunlugu.query.all()
    return render_template('is_gunlugu.html', isler=isler)

@is_gunlugu_bp.route('/is_ekle', methods=['GET', 'POST'])
def is_ekle():
    """İş günlüğü ekleme"""
    musteriler = Musteri.query.all()
    
    if request.method == 'POST':
        try:
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
            flash('İş günlüğü başarıyla eklendi!', 'success')
            return redirect(url_for('is_gunlugu.is_gunlugu'))
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'error')
    
    return render_template('is_ekle.html', musteriler=musteriler)

@is_gunlugu_bp.route('/is_onay/<int:is_id>', methods=['POST'])
def is_onay(is_id):
    """İş onaylama - otomatik teslimat oluştur"""
    is_gunlugu = IsGunlugu.query.get_or_404(is_id)
    musteri = Musteri.query.get(is_gunlugu.musteri_id)
    
    # İş durumunu onaylandı yap
    is_gunlugu.durum = 'Onaylandı'
    
    # En son revizyonu onayla
    son_revizyon = Revizyon.query.filter_by(is_gunlugu_id=is_id)\
        .order_by(Revizyon.revizyon_numarasi.desc()).first()
    if son_revizyon:
        son_revizyon.durum = 'Onaylandı'
    
    # Otomatik teslimat oluştur
    teslimat_kodu = generate_teslimat_kodu(musteri)
    teslimat = Teslimat(
        teslimat_kodu=teslimat_kodu,
        is_gunlugu_id=is_id,
        musteri_id=is_gunlugu.musteri_id,
        baslik=is_gunlugu.aciklama or is_gunlugu.proje,
        proje=is_gunlugu.proje,
        sorumlu_kisi=is_gunlugu.sorumlu_kisi,
        olusturma_tarihi=is_gunlugu.tarih,
        teslim_tarihi=date.today(),
        durum='Tamamlandı',
        aciklama=f"İş Kodu: {is_gunlugu.is_kodu} - Otomatik oluşturuldu"
    )
    db.session.add(teslimat)
    db.session.commit()
    
    flash(f'{is_gunlugu.is_kodu} onaylandı ve teslimat oluşturuldu ({teslimat_kodu})!', 'success')
    return redirect(url_for('teslimat.teslimat_duzenle', teslimat_id=teslimat.id))

@is_gunlugu_bp.route('/is_duzenle/<int:is_id>', methods=['GET', 'POST'])
def is_duzenle(is_id):
    """İş günlüğü düzenleme - cascade güncelleme"""
    is_gunlugu = IsGunlugu.query.get_or_404(is_id)
    
    if request.method == 'POST':
        try:
            # İş günlüğünü güncelle
            is_gunlugu.tarih = datetime.strptime(request.form['tarih'], '%Y-%m-%d').date()
            is_gunlugu.proje = request.form['proje']
            is_gunlugu.aktivite_turu = request.form['aktivite_turu']
            is_gunlugu.aciklama = request.form['aciklama']
            is_gunlugu.sorumlu_kisi = request.form['sorumlu_kisi']
            is_gunlugu.sure_dakika = int(request.form['sure_dakika'])
            is_gunlugu.etiketler = request.form['etiketler']
            
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
            return redirect(url_for('musteri.musteri_detay', musteri_id=is_gunlugu.musteri_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'error')
    
    musteriler = Musteri.query.all()
    return render_template('is_duzenle.html', is_gunlugu=is_gunlugu, musteriler=musteriler)
