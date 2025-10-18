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
    """Müşteri detay sayfası"""
    musteri = Musteri.query.get_or_404(musteri_id)
    teslimatlar = Teslimat.query.filter_by(musteri_id=musteri_id).all()
    sosyal_medyalar = SosyalMedya.query.filter_by(musteri_id=musteri_id).all()
    revizyonlar = Revizyon.query.filter_by(musteri_id=musteri_id).all()
    
    return render_template('musteri_detay.html',
                         musteri=musteri,
                         teslimatlar=teslimatlar,
                         sosyal_medyalar=sosyal_medyalar,
                         revizyonlar=revizyonlar)

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
