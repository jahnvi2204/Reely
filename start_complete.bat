@echo off
REM Reely Video Captioning API - Complete Windows Startup Script

echo.
echo ========================================
echo    Reely Video Captioning Platform
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo [INFO] Python and Node.js are installed
echo.

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg is not installed
    echo Please install FFmpeg from https://ffmpeg.org/download.html
    echo Add FFmpeg to your PATH environment variable
    echo.
    set /p continue="Continue without FFmpeg? (y/n): "
    if /i not "%continue%"=="y" (
        echo Exiting...
        pause
        exit /b 1
    )
) else (
    echo [INFO] FFmpeg is installed
)

echo.
echo ========================================
echo    Setting up Backend
echo ========================================

cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    copy env.example .env
    echo [WARNING] Please edit .env file with your configuration
)

REM Create required directories
echo [INFO] Creating required directories...
if not exist "uploads" mkdir uploads
if not exist "processed" mkdir processed
if not exist "processed\cache" mkdir processed\cache

echo [SUCCESS] Backend setup completed
echo.

echo ========================================
echo    Setting up Frontend
echo ========================================

cd ..\frontend

REM Install Node.js dependencies
echo [INFO] Installing Node.js dependencies...
npm install
if errorlevel 1 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
)

REM Check if .env.local file exists
if not exist ".env.local" (
    echo [INFO] Creating .env.local file from template...
    copy env.example .env.local
    echo [WARNING] Please edit .env.local file with your Firebase configuration
)

echo [SUCCESS] Frontend setup completed
echo.

echo ========================================
echo    Starting Services
echo ========================================

echo [INFO] Starting MongoDB...
start "MongoDB" cmd /k "mongod"
timeout /t 3 /nobreak >nul

echo [INFO] Starting Redis...
start "Redis" cmd /k "redis-server"
timeout /t 3 /nobreak >nul

echo [INFO] Starting Celery Worker...
cd ..\backend
call venv\Scripts\activate.bat
start "Celery Worker" cmd /k "celery -A app.tasks.worker worker --loglevel=info"

echo [INFO] Starting FastAPI Server...
start "FastAPI Server" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo [INFO] Starting React Development Server...
cd ..\frontend
start "React Dev Server" cmd /k "npm run dev"

echo.
echo ========================================
echo    Services Started Successfully!
echo ========================================
echo.
echo Backend API:     http://localhost:8000
echo API Docs:        http://localhost:8000/docs
echo Frontend App:    http://localhost:5173
echo Health Check:    http://localhost:8000/health
echo.
echo ========================================
echo    Next Steps
echo ========================================
echo.
echo 1. Configure Firebase Authentication:
echo    - Edit frontend\.env.local with your Firebase config
echo    - Enable Google Sign-In in Firebase Console
echo.
echo 2. Configure Backend Settings:
echo    - Edit backend\.env with your database settings
echo    - Adjust file storage and processing settings
echo.
echo 3. Test the Application:
echo    - Open http://localhost:5173 in your browser
echo    - Sign in with Google
echo    - Upload a test video
echo.
echo ========================================
echo    Troubleshooting
echo ========================================
echo.
echo If services fail to start:
echo 1. Check that MongoDB and Redis are installed and running
echo 2. Verify Python and Node.js versions are compatible
echo 3. Check firewall settings for ports 8000 and 5173
echo 4. Review error messages in the service windows
echo.
echo For more help, see the README.md files in each directory
echo.

pause
