from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from src.models import Revizyon, Musteri, Teslimat
from src.utils.database import db

revizyon_bp = Blueprint('revizyon', __name__)

@revizyon_bp.route('/revizyon_ekle', methods=['GET', 'POST'])
@revizyon_bp.route('/revizyon_ekle/<int:musteri_id>', methods=['GET', 'POST'])
def revizyon_ekle(musteri_id=None):
    """Revizyon ekleme"""
    if request.method == 'POST':
        try:
            revizyon = Revizyon(
                tarih=datetime.strptime(request.form['tarih'], '%Y-%m-%d').date(),
                musteri_id=int(request.form['musteri_id']),
                teslimat_id=int(request.form['teslimat_id']) if request.form['teslimat_id'] else None,
                revize_talep_eden=request.form['revize_talep_eden'],
                revize_konusu=request.form['revize_konusu'],
                durum='Bekliyor'
            )
            db.session.add(revizyon)
            db.session.commit()
            
            if request.headers.get('Content-Type', '').startswith('application/x-www-form-urlencoded'):
                return jsonify({'success': True})
            else:
                flash('Revizyon başarıyla eklendi!', 'success')
                if musteri_id:
                    return redirect(url_for('musteri.musteri_detay', musteri_id=musteri_id))
                return redirect(url_for('musteri.musteriler'))
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'error')
    
    musteriler = Musteri.query.filter_by(aktif=True).all()
    teslimatlar = Teslimat.query.all()
    return render_template('revizyon_ekle.html',
                         musteriler=musteriler,
                         teslimatlar=teslimatlar,
                         secili_musteri_id=musteri_id)
