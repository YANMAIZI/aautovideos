@echo off
setlocal EnableDelayedExpansion
title ViralCutter - Install

cd /d "%~dp0"

echo.
echo ==========================================
echo   ViralCutter - Install Dependencies
echo ==========================================
echo.

echo [STEP 0/7] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Python not found!
    echo   Download Python 3.10, 3.11 or 3.12 from https://www.python.org/downloads/
    echo   IMPORTANT: Check "Add Python to PATH" during install!
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo   [OK] Python %PY_VER% found

echo %PY_VER% | findstr /C:"3.14" >nul
if not errorlevel 1 (
    echo.
    echo   WARNING: Python 3.14 detected.
    echo   Some packages like torch, whisperx, mediapipe may NOT support it.
    echo   Recommended: use Python 3.10, 3.11 or 3.12 from python.org
    echo.
    echo   Press Enter to continue anyway, or Ctrl+C to cancel...
    pause >nul
)

echo.
echo [STEP 1/7] Creating virtual environment .venv...
if exist .venv\Scripts\activate.bat (
    echo   [OK] .venv already exists
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo   [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo   [OK] Virtual environment created
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo   [ERROR] Failed to activate .venv!
    pause
    exit /b 1
)
echo   [OK] Environment activated

echo.
echo [STEP 2/7] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel --quiet
echo   [OK] pip upgraded

echo.
echo [STEP 3/7] Installing core dependencies...
pip install yt-dlp ffmpeg-python numpy tqdm psutil deep-translator gradio fastapi uvicorn opencv-python google-genai --quiet
if errorlevel 1 (
    echo   [WARNING] Some core packages failed. Check your internet connection.
) else (
    echo   [OK] Core dependencies installed
)

echo.
echo [STEP 4/7] Installing g4f...
pip install g4f --quiet
if errorlevel 1 (
    echo   [WARNING] g4f not installed - some AI features unavailable
) else (
    echo   [OK] g4f installed
)

echo.
echo [STEP 5/7] Installing PyTorch...
nvidia-smi >nul 2>&1
if not errorlevel 1 (
    echo   NVIDIA GPU detected. Trying CUDA 12.1...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
    if errorlevel 1 (
        echo   CUDA 12.1 failed, trying CUDA 11.8...
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --quiet
        if errorlevel 1 (
            echo   CUDA failed, falling back to CPU version...
            pip install torch torchvision torchaudio --quiet
        ) else (
            echo   [OK] PyTorch with CUDA 11.8 installed
        )
    ) else (
        echo   [OK] PyTorch with CUDA 12.1 installed
    )
) else (
    echo   No GPU found. Installing CPU-only PyTorch...
    pip install torch torchvision torchaudio --quiet
    if errorlevel 1 (
        echo   [WARNING] PyTorch not installed - transcription unavailable
    ) else (
        echo   [OK] PyTorch CPU installed
    )
)

echo.
echo [STEP 6/7] Installing AI libraries - whisperx, mediapipe, insightface...
echo   This may take several minutes...

echo   Installing whisperx...
pip install whisperx --quiet 2>nul
if errorlevel 1 (
    echo   whisperx not on PyPI, trying GitHub...
    pip install git+https://github.com/m-bain/whisperX.git --quiet 2>nul
    if errorlevel 1 (
        echo   [WARNING] whisperx failed. Requires Python 3.10-3.12 plus PyTorch.
    ) else (
        echo   [OK] whisperx installed from GitHub
    )
) else (
    echo   [OK] whisperx installed
)

echo   Installing mediapipe...
pip install mediapipe --quiet 2>nul
if errorlevel 1 (
    echo   [WARNING] mediapipe failed. Requires Python 3.12 or lower.
) else (
    echo   [OK] mediapipe installed
)

echo   Installing onnxruntime...
nvidia-smi >nul 2>&1
if not errorlevel 1 (
    pip install onnxruntime-gpu --quiet 2>nul
    if errorlevel 1 (
        pip install onnxruntime --quiet 2>nul
    ) else (
        echo   [OK] onnxruntime-gpu installed
    )
) else (
    pip install onnxruntime --quiet 2>nul
)
python -c "import onnxruntime" >nul 2>&1
if errorlevel 1 (
    echo   [WARNING] onnxruntime failed
) else (
    echo   [OK] onnxruntime installed
)

echo   Installing insightface...
pip install insightface --quiet 2>nul
if errorlevel 1 (
    echo   [WARNING] insightface failed.
    echo   You may need Microsoft C++ Build Tools:
    echo   https://visualstudio.microsoft.com/visual-cpp-build-tools/
) else (
    echo   [OK] insightface installed
)

echo.
echo [STEP 7/7] Checking ffmpeg binary...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   -------------------------------------------
    echo   WARNING: ffmpeg NOT found in PATH!
    echo   ViralCutter requires ffmpeg to process video.
    echo.
    echo   Install via Windows terminal run as Admin:
    echo     winget install Gyan.FFmpeg
    echo.
    echo   OR download from https://ffmpeg.org/download.html
    echo   Unzip and add the bin folder to system PATH.
    echo   -------------------------------------------
) else (
    echo   [OK] ffmpeg found
)

echo.
echo ==========================================
echo   INSTALL SUMMARY
echo ==========================================

python -c "import yt_dlp" >nul 2>&1
if errorlevel 1 ( echo [FAIL] yt-dlp ) else ( echo [OK]   yt-dlp )

python -c "import ffmpeg" >nul 2>&1
if errorlevel 1 ( echo [FAIL] ffmpeg-python ) else ( echo [OK]   ffmpeg-python )

python -c "import numpy" >nul 2>&1
if errorlevel 1 ( echo [FAIL] numpy ) else ( echo [OK]   numpy )

python -c "import gradio" >nul 2>&1
if errorlevel 1 ( echo [FAIL] gradio ) else ( echo [OK]   gradio )

python -c "import cv2" >nul 2>&1
if errorlevel 1 ( echo [FAIL] opencv-python ) else ( echo [OK]   opencv-python )

python -c "import torch" >nul 2>&1
if errorlevel 1 ( echo [WARN] torch ) else ( echo [OK]   torch )

python -c "import whisperx" >nul 2>&1
if errorlevel 1 ( echo [WARN] whisperx ) else ( echo [OK]   whisperx )

python -c "import mediapipe" >nul 2>&1
if errorlevel 1 ( echo [WARN] mediapipe ) else ( echo [OK]   mediapipe )

python -c "import insightface" >nul 2>&1
if errorlevel 1 ( echo [WARN] insightface ) else ( echo [OK]   insightface )

python -c "import g4f" >nul 2>&1
if errorlevel 1 ( echo [WARN] g4f ) else ( echo [OK]   g4f )

echo.
echo ==========================================
echo   Done!
echo   Run run.bat to start console mode
echo   Run run_webui.bat for browser UI
echo.
echo   FAIL = must fix, run INSTALL.bat again
echo   WARN = optional feature unavailable
echo ==========================================
echo.
pause
endlocal
