#!/usr/bin/env python3
"""
Generate a Django SECRET_KEY
"""

import secrets
import string

def generate_secret_key(length=50):
    """Generate a random secret key"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("Generated Django SECRET_KEY:")
    print(f"SECRET_KEY={secret_key}")
    print("\nCopy this line to your .env file!")
