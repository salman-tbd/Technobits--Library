import secrets
import string

# Generate Django SECRET_KEY
alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
secret_key = ''.join(secrets.choice(alphabet) for _ in range(50))
print("Copy this SECRET_KEY to your .env file:")
print(f"SECRET_KEY={secret_key}")
