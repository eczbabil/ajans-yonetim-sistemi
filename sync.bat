@echo off
chcp 65001 >nul
cls
echo ========================================
echo   SISYPHOS AJANS - GitHub Sync
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Git durumunu kontrol ediyorum...
git status
echo.

set /p commit_msg="Commit mesajı (Enter = otomatik): "
if "%commit_msg%"=="" set commit_msg=Auto-sync: %date% %time%

echo.
echo [2/3] Değişiklikleri GitHub'a gönderiyorum...
git add .
git commit -m "%commit_msg%"
git push

echo.
echo ========================================
echo ✅ GitHub'a başarıyla gönderildi!
echo ========================================
echo.
echo ⏭️  SONRAKİ ADIM:
echo    1. PythonAnywhere'de Web tab'ı açın
echo    2. Reload butonuna tıklayın
echo.
echo Canlı adresiniz: https://oguzhandiscioglu.pythonanywhere.com
echo.
pause

