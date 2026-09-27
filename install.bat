@echo off
cd /d "%~dp0"

echo ============================
echo       ARTHUR V1
echo ============================

py -3.12 -m venv .venv

if errorlevel 1 (
    echo.
    echo Python 3.12 est necessaire.
    echo.
    pause
    exit
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip

pip install -r requirements.txt

echo.
echo ============================
echo Installation terminee !
echo ============================
echo.
echo Lance maintenant run_arthur.bat
echo.

pause
