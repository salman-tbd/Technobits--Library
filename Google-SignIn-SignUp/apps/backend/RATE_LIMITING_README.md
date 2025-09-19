# 🔒 **Enhanced Redis-Based Rate Limiting System**

## **Overview**

This is a comprehensive, production-ready rate limiting system for the Django authentication backend, inspired by the `@digiassistants.com/` project but enhanced with **Redis for superior performance** and additional security features.

## **🌟 Key Features**

### **Core Rate Limiting**
- ✅ **Redis-based storage** for high performance and scalability
- ✅ **Multiple time windows** (per minute, hour, day)
- ✅ **Per-IP and Per-User limits** with configurable thresholds
- ✅ **Action-specific limits** (login, register, 2FA, API, etc.)
- ✅ **Progressive delays** and intelligent blocking

### **Security Features**
- ✅ **IP blocking** with automatic and manual controls
- ✅ **Suspicious activity detection** and monitoring
- ✅ **Request logging** for security analysis
- ✅ **Configurable block rules** with regex pattern matching
- ✅ **Admin override capabilities**

### **Management & Monitoring**
- ✅ **Django admin interface** for configuration management
- ✅ **REST API endpoints** for programmatic access
- ✅ **Management commands** for administration
- ✅ **Security dashboard** with real-time statistics
- ✅ **Comprehensive logging** and audit trails

---

## **🚀 Quick Setup**

### **1. Install Dependencies**
```bash
# Install Redis
docker run -d -p 6379:6379 --name redis redis:latest

# Install Python packages
pip install -r requirements.txt
```

### **2. Update Django Settings**
The following configurations have been added to `settings.py`:
- Redis connection settings
- Cache configuration
- Rate limiting middleware

### **3. Run Migrations**
```bash
python manage.py migrate
```

### **4. Create Default Configuration**
```bash
python manage.py shell -c "
from authentication.models import RateLimitConfig
config = RateLimitConfig.objects.create(
    name='production',
    login_ip_limit_per_minute=5,
    login_user_limit_per_minute=3,
    is_active=True
)
print('Rate limiting configuration created!')
"
```

---

## **📊 Configuration**

### **Rate Limit Thresholds**

| **Action** | **IP Limits** | **User Limits** | **Description** |
|------------|---------------|-----------------|-----------------|
| **Login** | 5/min, 20/hr, 100/day | 3/min, 10/hr, 50/day | Authentication attempts |
| **Register** | 5/min, 20/hr, 100/day | 3/min, 10/hr, 50/day | Account creation |
| **2FA** | 10/min, 50/hr | 5/min, 20/hr | Two-factor authentication |
| **API** | 60/min, 1000/hr | 100/min, 2000/hr | General API requests |
| **Password Reset** | 5/min, 20/hr | 3/min, 10/hr | Password recovery |

### **Lockout Settings**
- **IP Lockout Duration**: 15 minutes (900 seconds)
- **User Lockout Duration**: 10 minutes (600 seconds)
- **Progressive Delays**: Enabled by default
- **Suspicious Activity Threshold**: 3 failed attempts

---

## **🔧 Components**

### **1. Core Rate Limiter (`rate_limiter.py`)**
```python
from authentication.rate_limiter import rate_limiter

# Check rate limits
is_limited, info = rate_limiter.check_rate_limit(
    request=request,
    action='login',
    user_identifier='user@example.com'
)

# Record request
rate_limiter.record_request(
    request=request,
    action='login',
    success=True
)
```

### **2. Middleware (`middleware.py`)**
- **`IPBlockMiddleware`**: Fast IP blocking check
- **`RateLimitMiddleware`**: Comprehensive rate limiting and logging

### **3. Decorators (`decorators.py`)**
```python
from authentication.decorators import login_rate_limit

@login_rate_limit
def my_login_view(request):
    # Your view logic here
    pass
```

### **4. Database Models**
- **`RateLimitConfig`**: Configuration management
- **`VisitorLog`**: Request logging and monitoring
- **`IPBlockRule`**: Blocking rule definitions
- **`BlockedIP`**: Active IP blocks

---

## **🛠️ Management Commands**

### **Clear Rate Limits**
```bash
# Clear all rate limiting data
python manage.py clear_rate_limits --all

# Clear specific IP
python manage.py clear_rate_limits --ip 192.168.1.100

# Clear specific user
python manage.py clear_rate_limits --user user@example.com

# Clear expired data only
python manage.py clear_rate_limits --expired
```

### **View Statistics**
```bash
# Show general statistics
python manage.py rate_limit_stats

# Show specific IP details
python manage.py rate_limit_stats --ip 192.168.1.100

# Show Redis status
python manage.py rate_limit_stats --redis
```

---

## **📡 API Endpoints**

### **Security Dashboard**
```bash
GET /auth/security/dashboard/?days=7
```
Returns comprehensive security statistics and trends.

### **Rate Limit Status**
```bash
GET /auth/security/rate-limit-status/
```
Returns current rate limit status for the requesting user/IP.

### **IP Management**
```bash
# Block IP
POST /auth/security/block-ip/
{
  "ip_address": "192.168.1.100",
  "reason": "Suspicious activity",
  "duration_hours": 24
}

# Unblock IP
POST /auth/security/unblock-ip/
{
  "ip_address": "192.168.1.100"
}
```

### **Visitor Logs**
```bash
GET /auth/security/visitor-logs/?page=1&suspicious_only=true
```
Returns filtered visitor logs with pagination.

---

## **🎯 Admin Interface**

Access the Django admin at `/admin/` to manage:

### **Rate Limit Configuration**
- Set custom thresholds for different actions
- Configure lockout durations
- Enable/disable progressive delays

### **Blocked IPs**
- View currently blocked IPs
- Manually block/unblock IP addresses
- Set permanent or temporary blocks
- Bulk actions for IP management

### **Visitor Logs**
- Monitor all requests in real-time
- Filter by IP, path, or suspicious activity
- Track authentication attempts
- Export logs for analysis

### **IP Block Rules**
- Create custom blocking rules
- Use regex patterns for path matching
- Set automatic blocking thresholds
- Configure email notifications

---

## **🚨 Security Features**

### **Automatic IP Blocking**
IPs are automatically blocked when they:
- Exceed rate limits repeatedly
- Match configured block rules
- Show suspicious behavior patterns
- Attempt brute force attacks

### **Progressive Delays**
Failed attempts result in increasing delays:
- 1st failure: No delay
- 2nd failure: 1 second
- 3rd failure: 2 seconds
- 4th+ failures: Exponential backoff

### **Suspicious Activity Detection**
The system monitors for:
- Multiple failed login attempts
- Rapid request patterns
- Access to sensitive endpoints
- Unusual geographic patterns

---

## **📈 Monitoring & Alerts**

### **Real-time Dashboard**
- Request volume trends
- Failed authentication statistics
- Top suspicious IP addresses
- Active blocks and recent activity

### **Log Analysis**
All requests are logged with:
- IP address and user agent
- Request path and method
- Authentication status
- Response codes and timing
- Geographic information (optional)

### **Performance Metrics**
- Redis response times
- Rate limit effectiveness
- Block accuracy rates
- False positive monitoring

---

## **⚡ Performance Optimizations**

### **Redis Optimizations**
- **Sorted sets** for efficient time-window queries
- **Automatic expiration** to prevent memory bloat
- **Connection pooling** for high concurrency
- **Key namespacing** for organization

### **Database Optimizations**
- **Indexed fields** for fast queries
- **Bulk operations** for log management
- **Periodic cleanup** of old records
- **Efficient pagination** for large datasets

---

## **🔧 Configuration Examples**

### **High Security Environment**
```python
RateLimitConfig.objects.create(
    name='high_security',
    login_ip_limit_per_minute=2,      # Very restrictive
    login_user_limit_per_minute=1,
    ip_lockout_duration=1800,         # 30 minutes
    suspicious_activity_threshold=1,   # Block after 1 failure
    is_active=True
)
```

### **High Traffic Environment**
```python
RateLimitConfig.objects.create(
    name='high_traffic',
    login_ip_limit_per_minute=20,     # More permissive
    api_ip_limit_per_minute=200,
    ip_lockout_duration=300,          # 5 minutes
    enable_progressive_delays=False,   # Disable delays
    is_active=True
)
```

---

## **🧪 Testing**

### **Automated Testing**
```bash
# Run the built-in test
python manage.py shell < authentication/test_rate_limiting.py
```

### **Manual Testing**
1. Make rapid login attempts to trigger rate limiting
2. Check Redis for rate limit keys
3. Verify IP blocking functionality
4. Test admin interface operations

### **Load Testing**
```bash
# Example with curl
for i in {1..10}; do
  curl -X POST http://localhost:8007/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}'
  echo "Request $i completed"
done
```

---

## **🚨 Troubleshooting**

### **Common Issues**

#### **Redis Connection Failed**
```bash
# Check Redis status
docker ps | grep redis
redis-cli ping

# Restart Redis
docker restart redis
```

#### **Rate Limits Not Working**
```bash
# Check middleware order in settings.py
# Verify Redis connectivity
python manage.py rate_limit_stats --redis

# Clear and reset
python manage.py clear_rate_limits --all
```

#### **Too Many False Positives**
```bash
# Adjust thresholds in admin
# Review visitor logs for patterns
# Update IP block rules
```

### **Debug Mode**
Enable detailed logging in `settings.py`:
```python
LOGGING = {
    'loggers': {
        'authentication': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

---

## **🔮 Future Enhancements**

### **Planned Features**
- Geographic IP blocking
- Machine learning-based anomaly detection
- Integration with external threat feeds
- Advanced rate limit algorithms
- Real-time notifications
- Mobile admin app

### **API Extensions**
- GraphQL endpoints
- Webhook notifications
- Third-party integrations
- Advanced analytics
- Custom rule engines

---

## **📝 Contributing**

When extending the rate limiting system:

1. **Follow the existing patterns** for consistency
2. **Add comprehensive tests** for new features
3. **Update documentation** and examples
4. **Consider performance implications** of changes
5. **Maintain backward compatibility** when possible

---

## **🎉 Success!**

You now have a **production-ready, Redis-based rate limiting system** that provides:

✅ **Enhanced Security** - Protection against brute force and spam attacks
✅ **High Performance** - Redis-based storage for millisecond response times  
✅ **Comprehensive Monitoring** - Real-time dashboards and detailed logging
✅ **Easy Management** - Django admin interface and API endpoints
✅ **Flexible Configuration** - Customizable thresholds and rules
✅ **Scalable Architecture** - Designed for high-traffic applications

**The system is now active and protecting your authentication endpoints!** 🚀

---

## **📞 Support**

For questions, issues, or enhancements:
- Review the Django admin interface
- Check the visitor logs for patterns
- Use management commands for troubleshooting
- Monitor the security dashboard for insights
