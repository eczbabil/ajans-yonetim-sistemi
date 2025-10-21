from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from src.models import Revizyon, Musteri, Teslimat
from src.utils.database import db

revizyon_bp = Blueprint('revizyon', __name__)

@revizyon_bp.route('/revizyon_ekle', methods=['GET', 'POST'])
@revizyon_bp.route('/revizyon_ekle/<int:musteri_id>', methods=['GET', 'POST'])
def revizyon_ekle(musteri_id=None):
    """Revizyon ekleme"""
    from src.models import IsGunlugu
    
    if request.method == 'POST':
        try:
            is_gunlugu_id = int(request.form['is_gunlugu_id']) if request.form.get('is_gunlugu_id') else None
            
            # Önceki revizyonun durumunu "Tekrar Revize Geldi" yap
            if is_gunlugu_id:
                onceki_revizyon = Revizyon.query.filter_by(is_gunlugu_id=is_gunlugu_id)\
                    .order_by(Revizyon.revizyon_numarasi.desc()).first()
                if onceki_revizyon:
                    onceki_revizyon.durum = 'Tekrar Revize Geldi'
                
                # İş günlüğü durumunu ve revizyon sayısını güncelle
                is_gunlugu = IsGunlugu.query.get(is_gunlugu_id)
                if is_gunlugu:
                    is_gunlugu.durum = 'Revizede'
                    is_gunlugu.revizyon_sayisi = (is_gunlugu.revizyon_sayisi or 0) + 1
                    revizyon_numarasi = is_gunlugu.revizyon_sayisi
                    baslik = f"Revizyon {revizyon_numarasi}"
                else:
                    revizyon_numarasi = 1
                    baslik = "Revizyon 1"
            else:
                revizyon_numarasi = 1
                baslik = "Revizyon 1"
            
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
            db.session.add(revizyon)
            db.session.commit()
            
            if request.headers.get('Content-Type', '').startswith('application/x-www-form-urlencoded'):
                return jsonify({'success': True})
            else:
                flash(f'{baslik} başarıyla eklendi!', 'success')
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
