"""
Veritabanini tamamen sifirlar ve yeniden olusturur
UYARI: Tum veriler silinecektir!
"""
import os
from app import app, db

def reset_database():
    print("=" * 60)
    print("UYARI: Tum veritabani silinecek!")
    print("=" * 60)
    onay = input("Devam etmek istediginize emin misiniz? (EVET yazin): ")
    
    if onay != "EVET":
        print("Islem iptal edildi.")
        return
    
    with app.app_context():
        # Veritabani dosyasinin yolunu al
        db_path = os.path.join(app.instance_path, 'ajans.db')
        
        # Eski veritabanini sil
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"Eski veritabani silindi: {db_path}")
            except Exception as e:
                print(f"Veritabani silinirken hata: {e}")
                print("Flask uygulamasini kapatip tekrar deneyin.")
                return
        
        # Yeni veritabanini olustur
        db.create_all()
        print("Yeni veritabani olusturuldu!")
        print("=" * 60)
        print("Islem tamamlandi. Sistem hazir!")
        print("=" * 60)

if __name__ == '__main__':
    reset_database()

