"""
Logging konfigürasyonu
Her kritik işlem için detaylı loglama
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(app):
    """Uygulama için logger konfigürasyonu"""
    
    # Logs klasörünü oluştur
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Log dosyası adı (tarihli)
    log_filename = f'logs/ajans_{datetime.now().strftime("%Y%m%d")}.log'
    
    # Program her başlatıldığında log dosyasını sıfırla
    try:
        if os.path.exists(log_filename):
            os.remove(log_filename)
    except PermissionError:
        # Dosya kullanımdaysa, üzerine yaz
        pass
    
    # File handler - dosyaya yazma
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # Console handler - konsola yazma
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # App logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Başlangıç logu
    app.logger.info('=' * 80)
    app.logger.info('AJANS YÖNETİM SİSTEMİ BAŞLATILDI')
    app.logger.info('=' * 80)
    
    return app.logger
