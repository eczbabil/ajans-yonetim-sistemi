from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from src.models import IsGunlugu, Musteri
from src.utils.database import db

is_gunlugu_bp = Blueprint('is_gunlugu', __name__)

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
