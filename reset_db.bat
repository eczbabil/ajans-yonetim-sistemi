@echo off
chcp 65001 >nul
echo ================================================
echo VERITABANI SIFIRLAMA ARACI
echo ================================================
echo.
echo UYARI: Bu islem tum verileri silecektir!
echo.
python reset_database.py
echo.
pause

