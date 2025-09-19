#!/usr/bin/env python3
"""
Setup script for PayPal Django + Next.js integration
"""
import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def setup_backend():
    """Set up Django backend"""
    print("\n🔧 Setting up Django Backend...")
    
    # Check if virtual environment exists
    if not Path("venv").exists():
        print("Creating virtual environment...")
        if not run_command("python -m venv venv"):
            return False
    
    # Activate virtual environment and install requirements
    venv_python = "venv\\Scripts\\python" if os.name == 'nt' else "venv/bin/python"
    venv_pip = "venv\\Scripts\\pip" if os.name == 'nt' else "venv/bin/pip"
    
    if not run_command(f"{venv_pip} install -r requirements.txt"):
        return False
    
    # Run migrations
    if not run_command(f"{venv_python} manage.py makemigrations"):
        return False
    
    if not run_command(f"{venv_python} manage.py migrate"):
        return False
    
    # Create .env file if it doesn't exist
    if not Path(".env").exists():
        if Path(".env.example").exists():
            if os.name == 'nt':
                run_command("copy .env.example .env")
            else:
                run_command("cp .env.example .env")
            print("📝 Created .env file from .env.example")
            print("⚠️  Please update .env with your PayPal credentials!")
    
    return True

def setup_frontend():
    """Set up Next.js frontend"""
    print("\n🔧 Setting up Next.js Frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install npm dependencies
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    # Create .env.local file if it doesn't exist
    env_local = frontend_dir / ".env.local"
    env_example = frontend_dir / ".env.local.example"
    
    if not env_local.exists() and env_example.exists():
        if os.name == 'nt':
            run_command("copy .env.local.example .env.local", cwd=frontend_dir)
        else:
            run_command("cp .env.local.example .env.local", cwd=frontend_dir)
        print("📝 Created .env.local file from .env.local.example")
        print("⚠️  Please update .env.local with your PayPal Client ID!")
    
    return True

def main():
    """Main setup function"""
    print("🚀 PayPal Integration Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    # Check if Node.js is available
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js is required but not found")
        print("Please install Node.js 16+ from https://nodejs.org/")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Update .env with your PayPal credentials")
    print("2. Update frontend/.env.local with your PayPal Client ID")
    print("3. Start Django: python manage.py runserver")
    print("4. Start Next.js: cd frontend && npm run dev")
    print("5. Visit http://localhost:3000 to test the integration")
    print("\n📖 For detailed instructions, see README.md")

if __name__ == "__main__":
    main()
