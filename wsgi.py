"""
WSGI yapılandırma dosyası
PythonAnywhere ve production ortamları için
"""

import sys
import os

# Proje dizinini Python path'ine ekle
project_home = '/home/yourusername/ajans_yonetim_sistemi'  # PythonAnywhere'de değiştirilecek
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Virtual environment'ı aktif et (PythonAnywhere'de gerekli değil)
# activate_this = os.path.join(project_home, '.venv', 'bin', 'activate_this.py')
# with open(activate_this) as file_:
#     exec(file_.read(), dict(__file__=activate_this))

# Environment variables yükle
from dotenv import load_dotenv
dotenv_path = os.path.join(project_home, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Flask uygulamasını import et
from app import app as application

# PythonAnywhere logging için
import logging
logging.basicConfig(level=logging.INFO)

