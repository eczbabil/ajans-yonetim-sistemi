from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_db(app):
    """Veritabanını başlat"""
    db.init_app(app)
    
    with app.app_context():
        # Tabloları oluştur
        db.create_all()
        
        # Uploads klasörünü oluştur
        uploads_dir = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'))
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
