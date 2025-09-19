"""
Simple test script to verify rate limiting functionality.
Run with: python manage.py shell < authentication/test_rate_limiting.py
"""
import time
import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from authentication.models import RateLimitConfig, BlockedIP
from authentication.rate_limiter import rate_limiter


def test_rate_limiting():
    """Test rate limiting functionality."""
    print("🔒 Testing Rate Limiting System...")
    
    # Create test configuration
    config, created = RateLimitConfig.objects.get_or_create(
        name="test_config",
        defaults={
            'login_ip_limit_per_minute': 3,  # Very low for testing
            'login_user_limit_per_minute': 2,
            'is_active': True,
        }
    )
    
    if created:
        print("✓ Created test rate limit configuration")
    else:
        print("✓ Using existing test configuration")
    
    # Test client
    client = Client()
    
    # Test login rate limiting
    print("\n--- Testing Login Rate Limiting ---")
    
    login_url = '/auth/login/'
    test_data = {
        'email': 'test@example.com',
        'password': 'wrongpassword123'
    }
    
    # Make several rapid requests
    for i in range(5):
        response = client.post(login_url, test_data, content_type='application/json')
        print(f"Request {i+1}: Status {response.status_code}")
        
        if response.status_code == 429:
            print(f"✓ Rate limit triggered after {i+1} attempts")
            break
        
        time.sleep(0.1)  # Small delay
    
    # Test Redis functionality
    print("\n--- Testing Redis Functionality ---")
    
    if rate_limiter.redis_client:
        try:
            # Test Redis connection
            rate_limiter.redis_client.ping()
            print("✓ Redis connection successful")
            
            # Check for rate limit keys
            keys = rate_limiter.redis_client.keys('rate_limit:*')
            print(f"✓ Found {len(keys)} rate limit keys in Redis")
            
            # Show some sample keys
            for key in keys[:3]:
                print(f"  - {key}")
                
        except Exception as e:
            print(f"✗ Redis error: {e}")
    else:
        print("⚠️ Redis not available")
    
    # Test IP blocking
    print("\n--- Testing IP Blocking ---")
    
    test_ip = "192.168.1.100"
    
    # Create a test block
    blocked_ip, created = BlockedIP.objects.get_or_create(
        ip_address=test_ip,
        defaults={
            'reason': 'Test block',
            'is_active': True,
            'attempt_count': 5,
        }
    )
    
    if created:
        print(f"✓ Created test IP block for {test_ip}")
    else:
        print(f"✓ IP block already exists for {test_ip}")
    
    # Test block detection
    is_blocked = rate_limiter._is_ip_blocked(test_ip)
    print(f"✓ IP block detection: {is_blocked}")
    
    # Clean up test block
    blocked_ip.delete()
    print("✓ Cleaned up test IP block")
    
    print("\n--- Testing Security Dashboard Data ---")
    
    try:
        from authentication.api_views import security_dashboard_view
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser
        
        # Create mock admin request
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.filter(is_superuser=True).first()
        
        if request.user:
            print("✓ Found admin user for testing")
            # This would normally be called via URL, but we can test the core functionality
            print("✓ Dashboard function exists and is importable")
        else:
            print("⚠️ No admin user found, create one with: python manage.py createsuperuser")
            
    except Exception as e:
        print(f"✗ Dashboard test error: {e}")
    
    print("\n--- Rate Limiting Test Complete ---")
    print("Next steps:")
    print("1. Install Redis: docker run -d -p 6379:6379 redis:latest")
    print("2. Run migrations: python manage.py migrate")
    print("3. Create superuser: python manage.py createsuperuser")
    print("4. Start server: python manage.py runserver 8007")
    print("5. Test endpoints manually or with frontend")


if __name__ == "__main__":
    test_rate_limiting()
