#!/bin/bash

# Reely Video Captioning API - Startup Script

echo "🎬 Starting Reely Video Captioning API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Check if required directories exist
echo "📁 Creating required directories..."
mkdir -p uploads
mkdir -p processed
mkdir -p processed/cache

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed. Please install FFmpeg:"
    echo "   Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    echo "   Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB is not running. Please start MongoDB:"
    echo "   sudo systemctl start mongod"
    echo "   or: mongod"
fi

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis is not running. Please start Redis:"
    echo "   sudo systemctl start redis"
    echo "   or: redis-server"
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the services:"
echo "   1. Start Celery worker: celery -A app.tasks.worker worker --loglevel=info"
echo "   2. Start FastAPI server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📚 API Documentation will be available at:"
echo "   - Interactive docs: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo ""
echo "🎯 Health check: http://localhost:8000/health"
