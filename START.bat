@echo off
title ViralCutter
cd /d "%~dp0"

echo Deleting broken .venv...
if exist .venv rmdir /s /q .venv

echo Creating fresh .venv with pip...
python -m venv .venv --upgrade-deps
if errorlevel 1 ( echo ERROR: python not found & pause & exit /b 1 )

call .venv\Scripts\activate.bat

echo Installing packages...
pip install yt-dlp ffmpeg-python numpy tqdm psutil deep-translator gradio fastapi uvicorn opencv-python google-genai g4f whisperx mediapipe onnxruntime-gpu torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet

echo.
echo Starting ViralCutter...
echo.
python main_improved.py
pause
