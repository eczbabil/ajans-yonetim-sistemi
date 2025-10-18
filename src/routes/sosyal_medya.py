from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from src.models import SosyalMedya, Musteri
from src.utils.database import db

sosyal_medya_bp = Blueprint('sosyal_medya', __name__)

@sosyal_medya_bp.route('/sosyal_medya')
def sosyal_medya():
    """Sosyal medya listesi"""
    sosyal_medyalar = SosyalMedya.query.all()
    return render_template('sosyal_medya.html', sosyal_medyalar=sosyal_medyalar)

@sosyal_medya_bp.route('/sosyal_medya_ekle', methods=['GET', 'POST'])
@sosyal_medya_bp.route('/sosyal_medya_ekle/<int:musteri_id>', methods=['GET', 'POST'])
def sosyal_medya_ekle(musteri_id=None):
    """Sosyal medya ekleme"""
    musteriler = Musteri.query.filter_by(aktif=True).all()
    
    if request.method == 'POST':
        try:
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
            flash('Sosyal medya kaydı başarıyla eklendi!', 'success')
            
            if musteri_id:
                return redirect(url_for('musteri.musteri_detay', musteri_id=musteri_id))
            return redirect(url_for('sosyal_medya.sosyal_medya'))
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'error')
    
    return render_template('sosyal_medya_ekle.html', musteriler=musteriler, secili_musteri_id=musteri_id)
