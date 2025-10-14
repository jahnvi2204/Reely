#!/bin/bash

# Reely Test Runner - Comprehensive Testing Script

echo ""
echo "========================================"
echo "   Reely Test Suite Runner"
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

# Function to run tests
run_tests() {
    local test_type=$1
    local test_dir=$2
    local test_command=$3
    
    echo ""
    echo "========================================"
    echo "   Running $test_type Tests"
    echo "========================================"
    
    cd $test_dir
    
    if [ -f "$test_command" ] || command -v $test_command &> /dev/null; then
        print_status "Starting $test_type tests..."
        
        if [ "$test_type" = "Backend" ]; then
            # Activate virtual environment for backend tests
            if [ -d "venv" ]; then
                source venv/bin/activate
            fi
            python -m pytest tests/ -v --tb=short
        else
            # Frontend tests
            npm test
        fi
        
        if [ $? -eq 0 ]; then
            print_success "$test_type tests passed!"
        else
            print_error "$test_type tests failed!"
            return 1
        fi
    else
        print_warning "$test_command not found, skipping $test_type tests"
    fi
    
    cd ..
}

# Function to run API tests
run_api_tests() {
    echo ""
    echo "========================================"
    echo "   Running API Integration Tests"
    echo "========================================"
    
    cd backend
    
    # Check if backend is running
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "Backend is running, starting API tests..."
        
        # Activate virtual environment
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
        
        python test_api.py
        
        if [ $? -eq 0 ]; then
            print_success "API tests passed!"
        else
            print_error "API tests failed!"
            return 1
        fi
    else
        print_warning "Backend is not running on localhost:8000"
        print_status "Please start the backend first:"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  uvicorn app.main:app --reload"
    fi
    
    cd ..
}

# Function to run linting
run_linting() {
    echo ""
    echo "========================================"
    echo "   Running Code Quality Checks"
    echo "========================================"
    
    # Backend linting
    print_status "Checking backend code quality..."
    cd backend
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Check if flake8 is installed
    if command -v flake8 &> /dev/null; then
        flake8 app/ --max-line-length=100 --ignore=E203,W503
        if [ $? -eq 0 ]; then
            print_success "Backend code quality check passed!"
        else
            print_warning "Backend code quality issues found"
        fi
    else
        print_warning "flake8 not installed, skipping backend linting"
    fi
    
    cd ..
    
    # Frontend linting
    print_status "Checking frontend code quality..."
    cd frontend
    
    if command -v npm &> /dev/null; then
        npm run lint
        if [ $? -eq 0 ]; then
            print_success "Frontend code quality check passed!"
        else
            print_warning "Frontend code quality issues found"
        fi
    else
        print_warning "npm not found, skipping frontend linting"
    fi
    
    cd ..
}

# Function to run security checks
run_security_checks() {
    echo ""
    echo "========================================"
    echo "   Running Security Checks"
    echo "========================================"
    
    # Backend security
    print_status "Checking backend security..."
    cd backend
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Check if safety is installed
    if command -v safety &> /dev/null; then
        safety check
        if [ $? -eq 0 ]; then
            print_success "Backend security check passed!"
        else
            print_warning "Backend security vulnerabilities found"
        fi
    else
        print_warning "safety not installed, skipping security check"
    fi
    
    cd ..
    
    # Frontend security
    print_status "Checking frontend security..."
    cd frontend
    
    if command -v npm &> /dev/null; then
        npm audit
        if [ $? -eq 0 ]; then
            print_success "Frontend security check passed!"
        else
            print_warning "Frontend security vulnerabilities found"
        fi
    else
        print_warning "npm not found, skipping frontend security check"
    fi
    
    cd ..
}

# Main execution
main() {
    local test_type=${1:-"all"}
    
    case $test_type in
        "backend")
            run_tests "Backend" "backend" "pytest"
            ;;
        "frontend")
            run_tests "Frontend" "frontend" "npm"
            ;;
        "api")
            run_api_tests
            ;;
        "lint")
            run_linting
            ;;
        "security")
            run_security_checks
            ;;
        "all")
            run_tests "Backend" "backend" "pytest"
            run_tests "Frontend" "frontend" "npm"
            run_api_tests
            run_linting
            run_security_checks
            ;;
        *)
            echo "Usage: $0 [backend|frontend|api|lint|security|all]"
            echo ""
            echo "Options:"
            echo "  backend   - Run backend unit tests"
            echo "  frontend  - Run frontend tests"
            echo "  api       - Run API integration tests"
            echo "  lint      - Run code quality checks"
            echo "  security  - Run security checks"
            echo "  all       - Run all tests (default)"
            exit 1
            ;;
    esac
    
    echo ""
    echo "========================================"
    echo "   Test Suite Completed"
    echo "========================================"
    echo ""
    print_success "All requested tests have been executed!"
    echo ""
    echo "For more detailed test results, check the individual test outputs above."
    echo "To run specific test categories, use: $0 [backend|frontend|api|lint|security]"
}

# Run main function with all arguments
main "$@"
