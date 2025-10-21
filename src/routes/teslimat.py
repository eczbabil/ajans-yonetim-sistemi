from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from src.models import Teslimat, Musteri
from src.utils.database import db

teslimat_bp = Blueprint('teslimat', __name__)

@teslimat_bp.route('/teslimatlar')
def teslimatlar():
    """Teslimat listesi"""
    teslimatlar = Teslimat.query.all()
    return render_template('teslimatlar.html', teslimatlar=teslimatlar)

@teslimat_bp.route('/teslimat_ekle', methods=['GET', 'POST'])
@teslimat_bp.route('/teslimat_ekle/<int:musteri_id>', methods=['GET', 'POST'])
def teslimat_ekle(musteri_id=None):
    """Teslimat ekleme"""
    musteriler = Musteri.query.all()
    
    if request.method == 'POST':
        try:
            teslimat = Teslimat(
                musteri_id=int(request.form['musteri_id']),
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
            flash('Teslimat başarıyla eklendi!', 'success')
            
            if musteri_id:
                return redirect(url_for('musteri.musteri_detay', musteri_id=musteri_id))
            return redirect(url_for('teslimat.teslimatlar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'error')
    
    return render_template('teslimat_ekle.html', musteriler=musteriler, secili_musteri_id=musteri_id)

@teslimat_bp.route('/teslimat_duzenle/<int:teslimat_id>', methods=['GET', 'POST'])
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
            flash(f'{teslimat.teslimat_kodu} başarıyla güncellendi!', 'success')
            return redirect(url_for('musteri.musteri_detay', musteri_id=teslimat.musteri_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'error')
    
    return render_template('teslimat_duzenle.html', teslimat=teslimat, musteriler=musteriler)