#!/bin/bash

# Movie Continuation System - Run Script
# Usage: ./scripts/run.sh [dev|prod|docker|stop]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Movie Continuation System${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f env.example ]; then
            cp env.example .env
            print_status "Created .env file from template. Please edit it with your API keys."
        else
            print_error "env.example not found. Please create a .env file manually."
            exit 1
        fi
    fi
}

# Install Python dependencies
install_deps() {
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    print_status "Dependencies installed successfully!"
}

# Run in development mode
run_dev() {
    print_header
    print_status "Starting in development mode..."
    
    check_python
    check_env
    install_deps
    
    print_status "Starting FastAPI backend..."
    python main.py &
    BACKEND_PID=$!
    
    sleep 3
    
    print_status "Starting Streamlit frontend..."
    cd frontend && streamlit run streamlit_app.py --server.port 8501 &
    FRONTEND_PID=$!
    
    print_status "System started successfully!"
    print_status "Backend: http://localhost:8000"
    print_status "Frontend: http://localhost:8501"
    print_status "API Docs: http://localhost:8000/docs"
    
    # Wait for user to stop
    echo ""
    print_warning "Press Ctrl+C to stop the system..."
    trap "cleanup_dev" INT
    wait
}

# Cleanup development processes
cleanup_dev() {
    print_status "Stopping development servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    print_status "Development servers stopped."
    exit 0
}

# Run in production mode (Docker)
run_prod() {
    print_header
    print_status "Starting in production mode (Docker)..."
    
    check_docker
    check_env
    
    print_status "Building and starting Docker containers..."
    docker-compose up --build -d
    
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        print_status "Backend is running!"
    else
        print_warning "Backend might still be starting..."
    fi
    
    if curl -f http://localhost:8501/ > /dev/null 2>&1; then
        print_status "Frontend is running!"
    else
        print_warning "Frontend might still be starting..."
    fi
    
    print_status "System started successfully!"
    print_status "Backend: http://localhost:8000"
    print_status "Frontend: http://localhost:8501"
    print_status "API Docs: http://localhost:8000/docs"
    
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: ./scripts/run.sh stop"
}

# Stop Docker containers
stop_docker() {
    print_status "Stopping Docker containers..."
    docker-compose down
    print_status "Docker containers stopped."
}

# Show logs
show_logs() {
    print_status "Showing Docker logs..."
    docker-compose logs -f
}

# Main script logic
case "${1:-dev}" in
    "dev")
        run_dev
        ;;
    "prod"|"docker")
        run_prod
        ;;
    "stop")
        stop_docker
        ;;
    "logs")
        show_logs
        ;;
    "help"|"-h"|"--help")
        print_header
        echo "Usage: $0 [dev|prod|docker|stop|logs|help]"
        echo ""
        echo "Commands:"
        echo "  dev     - Run in development mode (Python directly)"
        echo "  prod    - Run in production mode (Docker)"
        echo "  docker  - Same as prod"
        echo "  stop    - Stop Docker containers"
        echo "  logs    - Show Docker logs"
        echo "  help    - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 dev      # Start development servers"
        echo "  $0 prod     # Start production with Docker"
        echo "  $0 stop     # Stop Docker containers"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac 