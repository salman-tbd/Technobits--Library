@echo off
REM Docker Helper Script for Google SignIn/SignUp Project (Windows)
REM This script provides convenient commands for Docker operations

setlocal enabledelayedexpansion

REM Function to check if Docker is running
:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    exit /b 1
)
goto :eof

REM Function to show usage
:show_usage
echo Docker Helper Script for Google SignIn/SignUp Project
echo.
echo Usage: %~n0 [COMMAND]
echo.
echo Commands:
echo   start           Start all services in production mode
echo   start-dev       Start all services in development mode
echo   stop            Stop all services
echo   restart         Restart all services
echo   build           Build all services
echo   rebuild         Rebuild all services without cache
echo   logs            Show logs for all services
echo   logs-backend    Show backend logs
echo   logs-frontend   Show frontend logs
echo   shell-backend   Open shell in backend container
echo   shell-frontend  Open shell in frontend container
echo   migrate         Run Django migrations
echo   superuser       Create Django superuser
echo   clean           Clean up Docker resources
echo   status          Show container status
echo   help            Show this help message
echo.
goto :eof

REM Main script logic
if "%1"=="start" (
    call :check_docker
    echo [INFO] Starting services in production mode...
    docker-compose up -d --build
    echo [SUCCESS] Services started! Frontend: http://localhost:3003, Backend: http://localhost:8003
) else if "%1"=="start-dev" (
    call :check_docker
    echo [INFO] Starting services in development mode...
    docker-compose -f docker-compose.dev.yml up -d --build
    echo [SUCCESS] Development services started with hot reloading!
) else if "%1"=="stop" (
    call :check_docker
    echo [INFO] Stopping all services...
    docker-compose down
    docker-compose -f docker-compose.dev.yml down >nul 2>&1
    echo [SUCCESS] All services stopped.
) else if "%1"=="restart" (
    call :check_docker
    echo [INFO] Restarting services...
    docker-compose down
    docker-compose up -d --build
    echo [SUCCESS] Services restarted!
) else if "%1"=="build" (
    call :check_docker
    echo [INFO] Building all services...
    docker-compose build
    echo [SUCCESS] Build completed!
) else if "%1"=="rebuild" (
    call :check_docker
    echo [INFO] Rebuilding all services without cache...
    docker-compose build --no-cache
    echo [SUCCESS] Rebuild completed!
) else if "%1"=="logs" (
    call :check_docker
    docker-compose logs -f
) else if "%1"=="logs-backend" (
    call :check_docker
    docker-compose logs -f backend
) else if "%1"=="logs-frontend" (
    call :check_docker
    docker-compose logs -f frontend
) else if "%1"=="shell-backend" (
    call :check_docker
    echo [INFO] Opening shell in backend container...
    docker-compose exec backend /bin/bash
) else if "%1"=="shell-frontend" (
    call :check_docker
    echo [INFO] Opening shell in frontend container...
    docker-compose exec frontend /bin/sh
) else if "%1"=="migrate" (
    call :check_docker
    echo [INFO] Running Django migrations...
    docker-compose exec backend python manage.py migrate
    echo [SUCCESS] Migrations completed!
) else if "%1"=="superuser" (
    call :check_docker
    echo [INFO] Creating Django superuser...
    docker-compose exec backend python manage.py createsuperuser
) else if "%1"=="clean" (
    call :check_docker
    echo [WARNING] This will remove all stopped containers, unused networks, images, and build cache.
    set /p confirm="Are you sure? (y/N): "
    if /i "!confirm!"=="y" (
        echo [INFO] Cleaning up Docker resources...
        docker system prune -a -f
        echo [SUCCESS] Cleanup completed!
    ) else (
        echo [INFO] Cleanup cancelled.
    )
) else if "%1"=="status" (
    call :check_docker
    echo [INFO] Container status:
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
) else if "%1"=="help" (
    call :show_usage
) else if "%1"=="" (
    call :show_usage
) else (
    echo [ERROR] Unknown command: %1
    call :show_usage
    exit /b 1
)

