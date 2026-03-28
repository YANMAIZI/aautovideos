@echo off
setlocal
title ViralCutter - Windows 11 Start

cd /d "%~dp0"
set "VIRALCUTTER_LANG=ru_RU"

if not exist .venv\Scripts\activate.bat (
    echo.
    echo [ОШИБКА] Виртуальное окружение .venv не найдено.
    echo Сначала запустите INSTALL.bat
    echo.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

python -c "import yt_dlp, gradio, fastapi" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Зависимости не установлены.
    echo Запустите INSTALL.bat и повторите запуск.
    echo.
    pause
    exit /b 1
)

echo [OK] Запуск WebUI: http://127.0.0.1:7860
echo [OK] Язык интерфейса: Русский
python webui\app.py

echo.
pause
endlocal
