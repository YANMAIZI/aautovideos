@echo off
setlocal EnableDelayedExpansion
title ViralCutter - Установка (Windows 11)

cd /d "%~dp0"
set "VIRALCUTTER_LANG=ru_RU"

echo.
echo ==========================================
echo  ViralCutter: быстрая установка (Windows 11)
echo ==========================================
echo.

echo [1/6] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден.
    echo Установите Python 3.10-3.12: https://www.python.org/downloads/
    echo В установщике включите "Add Python to PATH".
    pause
    exit /b 1
)

echo [2/6] Создание .venv...
if not exist .venv\Scripts\activate.bat (
    python -m venv .venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать .venv
        pause
        exit /b 1
    )
)
call .venv\Scripts\activate.bat

echo [3/6] Обновление pip...
python -m pip install --upgrade pip setuptools wheel

echo [4/6] Установка основных зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Часть зависимостей не установилась.
    echo Проверьте интернет и повторите INSTALL.bat
)

echo [5/6] Проверка ffmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] ffmpeg не найден в PATH.
    echo Установите командой: winget install Gyan.FFmpeg
) else (
    echo [OK] ffmpeg найден.
)

echo [6/6] Готово.
echo Для запуска используйте START_WINDOWS_11.bat
echo.
pause
endlocal
