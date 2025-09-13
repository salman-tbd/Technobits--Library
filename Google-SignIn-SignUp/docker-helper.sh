#!/bin/bash

# Docker Helper Script for Google SignIn/SignUp Project
# This script provides convenient commands for Docker operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo "Docker Helper Script for Google SignIn/SignUp Project"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start           Start all services in production mode"
    echo "  start-dev       Start all services in development mode"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  build           Build all services"
    echo "  rebuild         Rebuild all services without cache"
    echo "  logs            Show logs for all services"
    echo "  logs-backend    Show backend logs"
    echo "  logs-frontend   Show frontend logs"
    echo "  shell-backend   Open shell in backend container"
    echo "  shell-frontend  Open shell in frontend container"
    echo "  migrate         Run Django migrations"
    echo "  superuser       Create Django superuser"
    echo "  clean           Clean up Docker resources"
    echo "  status          Show container status"
    echo "  help            Show this help message"
    echo ""
}

# Main script logic
case "$1" in
    "start")
        check_docker
        print_info "Starting services in production mode..."
        docker-compose up -d --build
        print_success "Services started! Frontend: http://localhost:3007, Backend: http://localhost:8007"
        ;;
    
    "start-dev")
        check_docker
        print_info "Starting services in development mode..."
        docker-compose -f docker-compose.dev.yml up -d --build
        print_success "Development services started with hot reloading!"
        ;;
    
    "stop")
        check_docker
        print_info "Stopping all services..."
        docker-compose down
        docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
        print_success "All services stopped."
        ;;
    
    "restart")
        check_docker
        print_info "Restarting services..."
        docker-compose down
        docker-compose up -d --build
        print_success "Services restarted!"
        ;;
    
    "build")
        check_docker
        print_info "Building all services..."
        docker-compose build
        print_success "Build completed!"
        ;;
    
    "rebuild")
        check_docker
        print_info "Rebuilding all services without cache..."
        docker-compose build --no-cache
        print_success "Rebuild completed!"
        ;;
    
    "logs")
        check_docker
        docker-compose logs -f
        ;;
    
    "logs-backend")
        check_docker
        docker-compose logs -f backend
        ;;
    
    "logs-frontend")
        check_docker
        docker-compose logs -f frontend
        ;;
    
    "shell-backend")
        check_docker
        print_info "Opening shell in backend container..."
        docker-compose exec backend /bin/bash
        ;;
    
    "shell-frontend")
        check_docker
        print_info "Opening shell in frontend container..."
        docker-compose exec frontend /bin/sh
        ;;
    
    "migrate")
        check_docker
        print_info "Running Django migrations..."
        docker-compose exec backend python manage.py migrate
        print_success "Migrations completed!"
        ;;
    
    "superuser")
        check_docker
        print_info "Creating Django superuser..."
        docker-compose exec backend python manage.py createsuperuser
        ;;
    
    "clean")
        check_docker
        print_warning "This will remove all stopped containers, unused networks, images, and build cache."
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Cleaning up Docker resources..."
            docker system prune -a -f
            print_success "Cleanup completed!"
        else
            print_info "Cleanup cancelled."
        fi
        ;;
    
    "status")
        check_docker
        print_info "Container status:"
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ;;
    
    "help"|"")
        show_usage
        ;;
    
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac

