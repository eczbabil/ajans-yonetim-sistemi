import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

class Config:
    """Ana konfigürasyon sınıfı"""
    SECRET_KEY = 'sisyphos_ajans_2025'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ajans.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = str(BASE_DIR / 'uploads')
    STATIC_FOLDER = str(BASE_DIR / 'static')
    TEMPLATE_FOLDER = str(BASE_DIR / 'templates')
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = str(BASE_DIR / 'logs' / 'app.log')
    
    @staticmethod
    def init_app(app):
        """Uygulama başlatma konfigürasyonu"""
        # Uploads klasörünü oluştur
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        # Logs klasörünü oluştur
        os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)

class DevelopmentConfig(Config):
    """Geliştirme ortamı konfigürasyonu"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ajans.db'

class ProductionConfig(Config):
    """Üretim ortamı konfigürasyonu"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ajans.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
