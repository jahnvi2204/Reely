@echo off
REM Reely Video Captioning API - Windows Startup Script

echo 🎬 Starting Reely Video Captioning API...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚙️  Creating .env file from template...
    copy env.example .env
    echo 📝 Please edit .env file with your configuration
)

REM Check if required directories exist
echo 📁 Creating required directories...
if not exist "uploads" mkdir uploads
if not exist "processed" mkdir processed
if not exist "processed\cache" mkdir processed\cache

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  FFmpeg is not installed. Please install FFmpeg:
    echo    Download from https://ffmpeg.org/download.html
    echo    Add to PATH environment variable
    pause
    exit /b 1
)

echo ✅ Setup complete!
echo.
echo 🚀 To start the services:
echo    1. Start Celery worker: celery -A app.tasks.worker worker --loglevel=info
echo    2. Start FastAPI server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 📚 API Documentation will be available at:
echo    - Interactive docs: http://localhost:8000/docs
echo    - ReDoc: http://localhost:8000/redoc
echo.
echo 🎯 Health check: http://localhost:8000/health
pause
