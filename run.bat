@echo off
chcp 65001 >nul
title Sisyphos Ajans Yönetim Sistemi

echo ========================================
echo    Sisyphos Ajans Yönetim Sistemi
echo ========================================
echo.

echo [1/4] Python dependencies yukleniyor...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Hata: Dependencies yuklenemedi!
    echo Python yuklu oldugundan emin olun.
    pause
    exit /b 1
)

echo.
echo [2/4] Veritabani tablolari olusturuluyor...
python -c "from app import app; app.app_context().push(); print('Veritabani hazir!')"

echo.
echo [3/4] Uploads klasoru olusturuluyor...
if not exist "uploads" mkdir uploads
echo Uploads klasoru hazir!

echo.
echo [4/4] Sunucu baslatiliyor...
echo.
echo ========================================
echo    Sistem http://localhost:5000 adresinde calisiyor
echo    Kapatmak icin CTRL+C tuslarina basin
echo ========================================
echo.

python app.py

pause