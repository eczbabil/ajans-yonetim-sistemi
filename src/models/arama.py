"""
Arama Kayıtları Modeli - CRM Modülü
Müşteri aramaları ve takibi için
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Arama(db.Model):
    """
    Müşteri arama kayıtları modeli
    CRM için arama takibi ve geri dönüş yönetimi
    """
    __tablename__ = 'arama'
    
    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.Date, nullable=False)
    musteri_id = db.Column(db.Integer, db.ForeignKey('musteri.id'))
    arayan_aranan = db.Column(db.String(100))  # Arayan veya aranan kişi
    konu = db.Column(db.Text)
    sonuc = db.Column(db.String(50))  # Not Alındı, Tamamlandı, Geri Dönülecek, Olumsuz
    sorumlu_kisi = db.Column(db.String(100))
    notlar = db.Column(db.Text)
    geri_donus_tarihi = db.Column(db.Date, nullable=True)
    durum = db.Column(db.String(20), default='Bekliyor')  # Bekliyor, Tamamlandı, İptal
    
    # İlişkiler
    musteri = db.relationship('Musteri', backref=db.backref('aramalar', lazy=True))
    
    def __repr__(self):
        return f'<Arama {self.id} - {self.musteri_id} - {self.tarih}>'
    
    def to_dict(self):
        """Model verisini dictionary'ye çevir"""
        return {
            'id': self.id,
            'tarih': self.tarih.strftime('%Y-%m-%d') if self.tarih else None,
            'musteri_id': self.musteri_id,
            'arayan_aranan': self.arayan_aranan,
            'konu': self.konu,
            'sonuc': self.sonuc,
            'sorumlu_kisi': self.sorumlu_kisi,
            'notlar': self.notlar,
            'geri_donus_tarihi': self.geri_donus_tarihi.strftime('%Y-%m-%d') if self.geri_donus_tarihi else None,
            'durum': self.durum
        }

