# Docker Setup Guide

This guide explains how to set up and run the Google SignIn/SignUp Authentication & Payment System using Docker.

## Prerequisites

- Docker Desktop installed on your system
- Docker Compose (usually included with Docker Desktop)
- Git (to clone the repository)

## Project Structure

The project consists of two main services:
- **Backend**: Django REST API running on port 8007
- **Frontend**: Next.js application running on port 3007

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Google-SignIn-SignUp
```

### 2. Environment Variables

Create a `.env` file in the root directory with your environment variables:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here

# reCAPTCHA (Optional)
RECAPTCHA_SECRET_KEY=your_recaptcha_secret_key
RECAPTCHA_SITE_KEY=your_recaptcha_site_key

# Email Service (Optional)
SENDINBLUE_API_KEY=your_sendinblue_api_key_here

# Payment Processing
GOOGLE_PAY_MERCHANT_ID=your_google_pay_merchant_id
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=sandbox

# Django Settings (Optional - defaults provided)
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### 3. Build and Run with Docker Compose

#### Production Mode

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode (background)
docker-compose up -d --build

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

#### Development Mode (with hot reloading)

```bash
# Build and start in development mode
docker-compose -f docker-compose.dev.yml up --build

# Run in detached mode
docker-compose -f docker-compose.dev.yml up -d --build

# Stop development services
docker-compose -f docker-compose.dev.yml down
```

### 4. Access the Application

- **Frontend**: http://localhost:3007
- **Backend API**: http://localhost:8007
- **Backend Admin**: http://localhost:8007/admin
- **Payment Demo**: http://localhost:3007/demos
- **Analytics Dashboard**: http://localhost:3007/analytics

## Docker Commands Reference

### Building Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend

# Build without cache
docker-compose build --no-cache
```

### Managing Services

```bash
# Start services
docker-compose up

# Start specific service
docker-compose up backend

# View logs
docker-compose logs
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f

# Execute commands in running container
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec frontend npm install new-package
```

### Database Management

```bash
# Run Django migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access Django shell
docker-compose exec backend python manage.py shell

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

## Docker Files Overview

### Backend Dockerfile (`apps/backend/Dockerfile`)
- Based on Python 3.11 slim image
- Installs Python dependencies from `requirements.txt`
- Runs Django development server on port 8007
- Includes static file collection

### Frontend Dockerfile (`apps/frontend/Dockerfile`)
- Multi-stage build for optimized production image
- Based on Node.js 18 Alpine image
- Uses Next.js standalone output for smaller image size
- Runs on port 3007

### Frontend Development Dockerfile (`apps/frontend/Dockerfile.dev`)
- Simple development setup with hot reloading
- Mounts source code as volume for live updates

## Environment Variables

### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `True` | Django debug mode |
| `SECRET_KEY` | Generated | Django secret key |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,backend` | Allowed hosts |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3007` | CORS allowed origins |
| `GOOGLE_CLIENT_ID` | Empty | Google OAuth client ID |
| `RECAPTCHA_SECRET_KEY` | Empty | reCAPTCHA secret key |
| `SENDINBLUE_API_KEY` | Empty | SendinBlue API key |
| `GOOGLE_PAY_MERCHANT_ID` | Empty | Google Pay merchant ID |
| `PAYPAL_CLIENT_ID` | Empty | PayPal client ID |
| `PAYPAL_CLIENT_SECRET` | Empty | PayPal client secret |
| `PAYPAL_MODE` | `sandbox` | PayPal mode (sandbox/live) |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | `15` | JWT access token lifetime |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | `7` | JWT refresh token lifetime |

### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `production` | Node environment |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8007` | Backend API URL |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Empty | Google OAuth client ID |
| `NEXT_PUBLIC_RECAPTCHA_SITE_KEY` | Empty | reCAPTCHA site key |
| `NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_ID` | Empty | Google Pay merchant ID |

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :3007
   netstat -tulpn | grep :8007
   
   # Kill the process or change ports in docker-compose.yml
   ```

2. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **Database Issues**
   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up --build
   ```

4. **Node Modules Issues**
   ```bash
   # Rebuild frontend
   docker-compose build --no-cache frontend
   ```

### Viewing Container Status

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View container resource usage
docker stats

# Inspect container
docker inspect google-auth-backend
docker inspect google-auth-frontend
```

### Cleaning Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a
```

## Development Workflow

1. **Start development environment**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Make code changes**: Files are automatically synced via volumes

3. **View logs**:
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f
   ```

4. **Run Django commands**:
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py test
   ```

5. **Install new packages**:
   ```bash
   # Backend
   docker-compose exec backend pip install new-package
   # Update requirements.txt manually
   
   # Frontend
   docker-compose exec frontend npm install new-package
   ```

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Use proper secret management
2. **Database**: Switch from SQLite to PostgreSQL/MySQL
3. **Static Files**: Use a proper static file server (nginx)
4. **SSL**: Configure HTTPS
5. **Monitoring**: Add logging and monitoring solutions

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify environment variables are set correctly
3. Ensure ports 3007 and 8007 are available
4. Try rebuilding: `docker-compose build --no-cache`

