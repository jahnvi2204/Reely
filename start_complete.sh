#!/bin/bash

# Reely Video Captioning API - Complete Linux/Mac Startup Script

echo ""
echo "========================================"
echo "   Reely Video Captioning Platform"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9+ from https://python.org"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.9"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python version $python_version is too old. Please install Python 3.9+"
    exit 1
fi

print_success "Python $python_version is installed"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed or not in PATH"
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

node_version=$(node --version)
print_success "Node.js $node_version is installed"

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    print_warning "FFmpeg is not installed"
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  CentOS/RHEL: sudo yum install ffmpeg"
    echo ""
    read -p "Continue without FFmpeg? (y/n): " continue_without_ffmpeg
    if [[ ! $continue_without_ffmpeg =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
else
    print_success "FFmpeg is installed"
fi

echo ""
echo "========================================"
echo "   Setting up Backend"
echo "========================================"

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install Python dependencies"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp env.example .env
    print_warning "Please edit .env file with your configuration"
fi

# Create required directories
print_status "Creating required directories..."
mkdir -p uploads
mkdir -p processed
mkdir -p processed/cache

print_success "Backend setup completed"

echo ""
echo "========================================"
echo "   Setting up Frontend"
echo "========================================"

cd ../frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install
if [ $? -ne 0 ]; then
    print_error "Failed to install Node.js dependencies"
    exit 1
fi

# Check if .env.local file exists
if [ ! -f ".env.local" ]; then
    print_status "Creating .env.local file from template..."
    cp env.example .env.local
    print_warning "Please edit .env.local file with your Firebase configuration"
fi

print_success "Frontend setup completed"

echo ""
echo "========================================"
echo "   Starting Services"
echo "========================================"

# Function to check if a service is running
check_service() {
    local service_name=$1
    local port=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "$service_name is already running on port $port"
        return 1
    fi
    return 0
}

# Start MongoDB
print_status "Starting MongoDB..."
if command -v mongod &> /dev/null; then
    if check_service "MongoDB" 27017; then
        mongod --fork --logpath /tmp/mongod.log
        sleep 2
    fi
else
    print_warning "MongoDB not found. Please install and start MongoDB manually"
fi

# Start Redis
print_status "Starting Redis..."
if command -v redis-server &> /dev/null; then
    if check_service "Redis" 6379; then
        redis-server --daemonize yes
        sleep 2
    fi
else
    print_warning "Redis not found. Please install and start Redis manually"
fi

# Start Celery Worker
print_status "Starting Celery Worker..."
cd ../backend
source venv/bin/activate
nohup celery -A app.tasks.worker worker --loglevel=info > celery.log 2>&1 &
CELERY_PID=$!
echo $CELERY_PID > celery.pid
sleep 2

# Start FastAPI Server
print_status "Starting FastAPI Server..."
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > fastapi.log 2>&1 &
FASTAPI_PID=$!
echo $FASTAPI_PID > fastapi.pid
sleep 2

# Start React Development Server
print_status "Starting React Development Server..."
cd ../frontend
nohup npm run dev > react.log 2>&1 &
REACT_PID=$!
echo $REACT_PID > react.pid
sleep 5

echo ""
echo "========================================"
echo "   Services Started Successfully!"
echo "========================================"
echo ""
echo "Backend API:     http://localhost:8000"
echo "API Docs:        http://localhost:8000/docs"
echo "Frontend App:    http://localhost:5173"
echo "Health Check:    http://localhost:8000/health"
echo ""
echo "========================================"
echo "   Next Steps"
echo "========================================"
echo ""
echo "1. Configure Firebase Authentication:"
echo "   - Edit frontend/.env.local with your Firebase config"
echo "   - Enable Google Sign-In in Firebase Console"
echo ""
echo "2. Configure Backend Settings:"
echo "   - Edit backend/.env with your database settings"
echo "   - Adjust file storage and processing settings"
echo ""
echo "3. Test the Application:"
echo "   - Open http://localhost:5173 in your browser"
echo "   - Sign in with Google"
echo "   - Upload a test video"
echo ""
echo "========================================"
echo "   Service Management"
echo "========================================"
echo ""
echo "To stop services:"
echo "  ./stop_services.sh"
echo ""
echo "To view logs:"
echo "  tail -f backend/celery.log"
echo "  tail -f backend/fastapi.log"
echo "  tail -f frontend/react.log"
echo ""
echo "Process IDs saved in:"
echo "  backend/celery.pid"
echo "  backend/fastapi.pid"
echo "  frontend/react.pid"
echo ""
echo "========================================"
echo "   Troubleshooting"
echo "========================================"
echo ""
echo "If services fail to start:"
echo "1. Check that MongoDB and Redis are installed and running"
echo "2. Verify Python and Node.js versions are compatible"
echo "3. Check firewall settings for ports 8000 and 5173"
echo "4. Review error messages in the log files"
echo ""
echo "For more help, see the README.md files in each directory"
echo ""

# Create stop script
cat > stop_services.sh << 'EOF'
#!/bin/bash

echo "Stopping Reely services..."

# Stop Celery Worker
if [ -f backend/celery.pid ]; then
    CELERY_PID=$(cat backend/celery.pid)
    if kill -0 $CELERY_PID 2>/dev/null; then
        kill $CELERY_PID
        echo "Stopped Celery Worker (PID: $CELERY_PID)"
    fi
    rm backend/celery.pid
fi

# Stop FastAPI Server
if [ -f backend/fastapi.pid ]; then
    FASTAPI_PID=$(cat backend/fastapi.pid)
    if kill -0 $FASTAPI_PID 2>/dev/null; then
        kill $FASTAPI_PID
        echo "Stopped FastAPI Server (PID: $FASTAPI_PID)"
    fi
    rm backend/fastapi.pid
fi

# Stop React Development Server
if [ -f frontend/react.pid ]; then
    REACT_PID=$(cat frontend/react.pid)
    if kill -0 $REACT_PID 2>/dev/null; then
        kill $REACT_PID
        echo "Stopped React Dev Server (PID: $REACT_PID)"
    fi
    rm frontend/react.pid
fi

# Stop MongoDB
if pgrep mongod > /dev/null; then
    pkill mongod
    echo "Stopped MongoDB"
fi

# Stop Redis
if pgrep redis-server > /dev/null; then
    pkill redis-server
    echo "Stopped Redis"
fi

echo "All services stopped."
EOF

chmod +x stop_services.sh

echo "Created stop_services.sh script"
echo ""
echo "Press Ctrl+C to exit this script (services will continue running)"
echo ""

# Keep script running and show status
while true; do
    echo -n "."
    sleep 10
done
