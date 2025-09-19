#!/usr/bin/env python3
"""
Quick setup script for Google Pay Integration
"""

import os
import subprocess
import sys

def create_env_file(file_path, template_content):
    """Create environment file if it doesn't exist"""
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write(template_content)
        print(f"Created {file_path}")
        print(f"Please edit {file_path} with your actual configuration")
    else:
        print(f"{file_path} already exists, skipping...")

def main():
    print("🚀 Setting up Google Pay Integration...")
    
    # Frontend .env.local template
    frontend_env = """# Google Pay Configuration
NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_ID=your_actual_merchant_id_here
NEXT_PUBLIC_GOOGLE_PAY_ENVIRONMENT=TEST
NEXT_PUBLIC_GOOGLE_PAY_MERCHANT_NAME=Your Business Name
"""

    # Backend .env template
    backend_env = """# Django Settings
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Pay
GOOGLE_PAY_MERCHANT_ID=your_actual_merchant_id_here
"""

    # Create environment files
    create_env_file('frontend/.env.local', frontend_env)
    create_env_file('backend/.env', backend_env)
    
    print("\n📝 Next steps:")
    print("1. Edit frontend/.env.local with your Google Pay merchant ID")
    print("2. Edit backend/.env with your Google Pay merchant ID")
    print("3. Run the backend: cd backend && python manage.py runserver")
    print("4. Run the frontend: cd frontend && npm run dev")
    print("\n📚 See ENVIRONMENT_SETUP.md for detailed configuration instructions")
    print("🔗 Get Google Pay Merchant ID: https://pay.google.com/business/console")

if __name__ == "__main__":
    main()