@echo off
setlocal
title ViralCutter WebUI

cd /d "%~dp0"

if not exist .venv\Scripts\activate.bat (
    echo.
    echo  [ERROR] Virtual environment not found! Run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
echo  [OK] Starting WebUI... Open browser at http://127.0.0.1:7860
echo.
python webui\app.py
pause
endlocal
