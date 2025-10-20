@echo off
chcp 65001 >nul
cls
echo ========================================
echo   SISYPHOS AJANS - Auto Deploy
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Git durumunu kontrol ediyorum...
git status
echo.

set /p commit_msg="Commit mesajı (Enter = otomatik): "
if "%commit_msg%"=="" set commit_msg=Auto-deploy: %date% %time%

echo.
echo [2/4] Değişiklikleri GitHub'a gönderiyorum...
git add .
git commit -m "%commit_msg%"
git push

echo.
echo [3/4] PythonAnywhere'de SSH ile güncelleme yapılıyor...
echo.
echo ⚠️  NOT: PythonAnywhere'de şu komutları çalıştırmanız gerekiyor:
echo.
echo    ssh oguzhandiscioglu@ssh.pythonanywhere.com
echo    cd /home/oguzhandiscioglu/ajans-yonetim-sistemi
echo    git pull origin main
echo    pip install --user -r requirements.txt
echo.
echo VEYA: Web interface'den Reload butonuna basın
echo    https://www.pythonanywhere.com/user/oguzhandiscioglu/webapps/
echo.
echo ========================================
echo ✅ GitHub'a başarıyla gönderildi!
echo ========================================
echo.
echo 🌐 Canlı adresiniz: https://oguzhandiscioglu.pythonanywhere.com
echo.
pause

