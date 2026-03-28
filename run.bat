@echo off
setlocal
title ViralCutter

cd /d "%~dp0"

if not exist .venv\Scripts\activate.bat (
    echo.
    echo  [ERROR] Virtual environment .venv not found!
    echo  Please run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

python -c "import yt_dlp" >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERROR] Dependencies not installed (yt_dlp missing)!
    echo  Please run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

echo  [OK] Starting ViralCutter...
echo.
python main_improved.py %*
echo.
pause
endlocal
