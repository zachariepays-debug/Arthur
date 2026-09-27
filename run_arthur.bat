@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Arthur n'est pas encore installe.
    echo Lance install.bat d'abord.
    pause
    exit
)

call .venv\Scripts\activate.bat

streamlit run app.py

pause
