"""
İstatistik ve metrik hesaplama fonksiyonları
Dashboard ve raporlama için kullanılır
"""

from datetime import datetime, timedelta
from sqlalchemy import func, extract
from flask import current_app


def get_dashboard_metrics(db):
    """
    Dashboard için temel metrikleri hesaplar
    
    Returns:
        dict: Metrikler dictionary'si
    """
    # Modeller app.py'de tanımlı, oradan import edelim
    from app import Musteri, IsGunlugu, Teslimat, SosyalMedya
    
    # Bugünün tarihi
    today = datetime.now()
    current_month_start = datetime(today.year, today.month, 1)
    
    # Toplam müşteri sayısı
    toplam_musteri = db.session.query(Musteri).count()
    
    # Bu ayki iş sayısı
    bu_ay_is = db.session.query(IsGunlugu).filter(
        IsGunlugu.tarih >= current_month_start.date()
    ).count()
    
    # Onaylanan teslimatlar
    onaylanan_teslimat = db.session.query(Teslimat).filter(
        Teslimat.durum == 'Onaylandı'
    ).count()
    
    # Toplam çalışma saati (dakikadan saate)
    toplam_dakika = db.session.query(func.sum(IsGunlugu.sure_dakika)).scalar() or 0
    toplam_saat = round(toplam_dakika / 60, 1)
    
    # Reels sayısı
    reels_sayisi = db.session.query(SosyalMedya).filter(
        SosyalMedya.gonderi_turu == 'Reels'
    ).count()
    
    # Bekleyen teslimatlar
    bekleyen_teslimat = db.session.query(Teslimat).filter(
        Teslimat.durum.in_(['Hazırlanıyor', 'Bekliyor', 'Revizede'])
    ).count()
    
    # Bu ayki toplam çalışma saati
    bu_ay_dakika = db.session.query(func.sum(IsGunlugu.sure_dakika)).filter(
        IsGunlugu.tarih >= current_month_start.date()
    ).scalar() or 0
    bu_ay_saat = round(bu_ay_dakika / 60, 1)
    
    return {
        'toplam_musteri': toplam_musteri,
        'bu_ay_is': bu_ay_is,
        'onaylanan_teslimat': onaylanan_teslimat,
        'toplam_saat': toplam_saat,
        'reels_sayisi': reels_sayisi,
        'bekleyen_teslimat': bekleyen_teslimat,
        'bu_ay_saat': bu_ay_saat
    }


def get_is_tipi_dagilimi(db, start_date=None, end_date=None):
    """
    İş tipi dağılımını hesaplar
    
    Args:
        db: Database session
        start_date: Başlangıç tarihi (opsiyonel)
        end_date: Bitiş tarihi (opsiyonel)
    
    Returns:
        dict: İş tipi ve adetleri
    """
    from app import IsGunlugu
    
    query = db.session.query(
        IsGunlugu.aktivite_turu,
        func.count(IsGunlugu.id).label('adet')
    )
    
    if start_date:
        query = query.filter(IsGunlugu.tarih >= start_date)
    if end_date:
        query = query.filter(IsGunlugu.tarih <= end_date)
    
    query = query.group_by(IsGunlugu.aktivite_turu).all()
    
    result = {}
    for aktivite, adet in query:
        if aktivite:
            result[aktivite] = adet
    
    return result


def get_gunluk_is_adedi(db, days=30):
    """
    Son N günün günlük iş adedini hesaplar
    
    Args:
        db: Database session
        days: Kaç günlük veri (varsayılan 30)
    
    Returns:
        dict: Tarih ve iş adedi
    """
    from app import IsGunlugu
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    query = db.session.query(
        IsGunlugu.tarih,
        func.count(IsGunlugu.id).label('adet')
    ).filter(
        IsGunlugu.tarih >= start_date,
        IsGunlugu.tarih <= end_date
    ).group_by(IsGunlugu.tarih).order_by(IsGunlugu.tarih).all()
    
    result = {}
    for tarih, adet in query:
        result[tarih.strftime('%Y-%m-%d')] = adet
    
    return result


def get_kisi_basi_is_sayisi(db, limit=10):
    """
    Kişi başı iş sayısını hesaplar (Top N)
    
    Args:
        db: Database session
        limit: Kaç kişi gösterilsin (varsayılan 10)
    
    Returns:
        list: [(kişi_adı, iş_sayısı), ...]
    """
    from app import IsGunlugu
    
    query = db.session.query(
        IsGunlugu.sorumlu_kisi,
        func.count(IsGunlugu.id).label('adet')
    ).filter(
        IsGunlugu.sorumlu_kisi.isnot(None),
        IsGunlugu.sorumlu_kisi != ''
    ).group_by(IsGunlugu.sorumlu_kisi).order_by(func.count(IsGunlugu.id).desc()).limit(limit).all()
    
    return [(kisi, adet) for kisi, adet in query]


def get_musteri_bazi_metrikler(db, musteri_id=None, start_date=None, end_date=None):
    """
    Müşteri bazlı metrikleri hesaplar
    
    Args:
        db: Database session
        musteri_id: Belirli bir müşteri ID (opsiyonel)
        start_date: Başlangıç tarihi (opsiyonel)
        end_date: Bitiş tarihi (opsiyonel)
    
    Returns:
        list: [(müşteri_adı, iş_sayısı, toplam_saat), ...]
    """
    from app import IsGunlugu, Musteri
    
    query = db.session.query(
        Musteri.ad,
        func.count(IsGunlugu.id).label('is_sayisi'),
        func.sum(IsGunlugu.sure_dakika).label('toplam_dakika')
    ).join(IsGunlugu, Musteri.id == IsGunlugu.musteri_id)
    
    if musteri_id:
        query = query.filter(Musteri.id == musteri_id)
    if start_date:
        query = query.filter(IsGunlugu.tarih >= start_date)
    if end_date:
        query = query.filter(IsGunlugu.tarih <= end_date)
    
    query = query.group_by(Musteri.ad).order_by(func.count(IsGunlugu.id).desc()).all()
    
    result = []
    for musteri_ad, is_sayisi, toplam_dakika in query:
        toplam_saat = round((toplam_dakika or 0) / 60, 1)
        result.append((musteri_ad, is_sayisi, toplam_saat))
    
    return result


def get_aylik_ozet(db, year=None, month=None):
    """
    Aylık özet raporu
    
    Args:
        db: Database session
        year: Yıl (varsayılan: bu yıl)
        month: Ay (varsayılan: bu ay)
    
    Returns:
        dict: Aylık özet metrikleri
    """
    from app import IsGunlugu, Teslimat
    
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month
    
    # Ayın ilk ve son günü
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    
    start_date = datetime(year, month, 1).date()
    end_date = (next_month - timedelta(days=1)).date()
    
    # İş sayısı
    is_sayisi = db.session.query(IsGunlugu).filter(
        IsGunlugu.tarih >= start_date,
        IsGunlugu.tarih <= end_date
    ).count()
    
    # Toplam çalışma saati
    toplam_dakika = db.session.query(func.sum(IsGunlugu.sure_dakika)).filter(
        IsGunlugu.tarih >= start_date,
        IsGunlugu.tarih <= end_date
    ).scalar() or 0
    
    # Tamamlanan teslimatlar
    tamamlanan = db.session.query(Teslimat).filter(
        Teslimat.teslim_tarihi >= start_date,
        Teslimat.teslim_tarihi <= end_date,
        Teslimat.durum == 'Onaylandı'
    ).count()
    
    return {
        'yil': year,
        'ay': month,
        'is_sayisi': is_sayisi,
        'toplam_saat': round(toplam_dakika / 60, 1),
        'tamamlanan_teslimat': tamamlanan
    }


def get_teslimat_durum_dagilimi(db):
    """
    Teslimat durum dağılımını hesaplar
    
    Returns:
        dict: Durum ve adetleri
    """
    from app import Teslimat
    
    query = db.session.query(
        Teslimat.durum,
        func.count(Teslimat.id).label('adet')
    ).group_by(Teslimat.durum).all()
    
    result = {}
    for durum, adet in query:
        if durum:
            result[durum] = adet
    
    return result

