from flask import Blueprint, render_template
from src.models import Musteri, Teslimat, IsGunlugu, SosyalMedya
from src.utils.database import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ana sayfa"""
    toplam_musteri = Musteri.query.count()
    toplam_teslimat = Teslimat.query.count()
    onaylanan_teslimat = Teslimat.query.filter_by(durum='Onaylandı').count()
    toplam_saat = db.session.query(db.func.sum(IsGunlugu.sure_dakika)).scalar() or 0
    
    # Reels sayısı hesapla
    reels_sayisi = SosyalMedya.query.filter_by(gonderi_turu='Reels').count()
    
    return render_template('index.html',
                         toplam_musteri=toplam_musteri,
                         toplam_teslimat=toplam_teslimat,
                         onaylanan_teslimat=onaylanan_teslimat,
                         toplam_saat=round(toplam_saat / 60, 1),
                         reels_sayisi=reels_sayisi)
