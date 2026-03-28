@echo off
setlocal
title ViralCutter - Check Environment

cd /d "%~dp0"

echo.
echo ==========================================
echo   ViralCutter - Environment Check
echo ==========================================
echo.

echo [SYSTEM]
python --version 2>nul
if errorlevel 1 echo   Python: NOT FOUND

ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo   ffmpeg: NOT FOUND - required for video processing!
) else (
    echo   ffmpeg: OK
)
echo.

echo [VIRTUAL ENVIRONMENT]
if exist .venv\Scripts\activate.bat (
    echo   .venv: found
    call .venv\Scripts\activate.bat
    echo   activated: OK
) else (
    echo   .venv: NOT FOUND - run INSTALL.bat
    echo.
    pause
    exit /b 1
)
echo.

echo [REQUIRED PACKAGES]
python -c "import yt_dlp; print('  yt-dlp:        OK')" >nul 2>&1
if errorlevel 1 ( echo   yt-dlp:        FAIL - run INSTALL.bat ) else ( echo   yt-dlp:        OK )

python -c "import ffmpeg" >nul 2>&1
if errorlevel 1 ( echo   ffmpeg-python: FAIL ) else ( echo   ffmpeg-python: OK )

python -c "import numpy" >nul 2>&1
if errorlevel 1 ( echo   numpy:         FAIL ) else ( echo   numpy:         OK )

python -c "import cv2" >nul 2>&1
if errorlevel 1 ( echo   opencv:        FAIL ) else ( echo   opencv:        OK )

python -c "import gradio" >nul 2>&1
if errorlevel 1 ( echo   gradio:        FAIL ) else ( echo   gradio:        OK )

python -c "import fastapi" >nul 2>&1
if errorlevel 1 ( echo   fastapi:       FAIL ) else ( echo   fastapi:       OK )

python -c "import tqdm" >nul 2>&1
if errorlevel 1 ( echo   tqdm:          FAIL ) else ( echo   tqdm:          OK )

python -c "import psutil" >nul 2>&1
if errorlevel 1 ( echo   psutil:        FAIL ) else ( echo   psutil:        OK )

echo.
echo [OPTIONAL AI PACKAGES]
python -c "import torch; print('  torch: OK CUDA=' + str(__import__('torch').cuda.is_available()))" >nul 2>&1
if errorlevel 1 ( echo   torch:       WARN - transcription unavailable ) else ( echo   torch:       OK )

python -c "import whisperx" >nul 2>&1
if errorlevel 1 ( echo   whisperx:    WARN - transcription unavailable ) else ( echo   whisperx:    OK )

python -c "import mediapipe" >nul 2>&1
if errorlevel 1 ( echo   mediapipe:   WARN - face tracking unavailable ) else ( echo   mediapipe:   OK )

python -c "import insightface" >nul 2>&1
if errorlevel 1 ( echo   insightface: WARN - face recognition unavailable ) else ( echo   insightface: OK )

python -c "import onnxruntime" >nul 2>&1
if errorlevel 1 ( echo   onnxruntime: WARN ) else ( echo   onnxruntime:  OK )

python -c "import g4f" >nul 2>&1
if errorlevel 1 ( echo   g4f:         WARN - GPT4Free unavailable ) else ( echo   g4f:         OK )

echo.
echo ==========================================
echo  FAIL = reinstall needed (run INSTALL.bat)
echo  WARN = optional feature unavailable
echo ==========================================
echo.
pause
endlocal
