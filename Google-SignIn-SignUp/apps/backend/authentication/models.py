from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from cryptography.fernet import Fernet
import hashlib
import secrets
import base64
import os
import time


class UserTwoFactor(models.Model):
    """Model to store Two-Factor Authentication settings for users."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor')
    is_enabled = models.BooleanField(default=False)
    secret_key_encrypted = models.TextField(blank=True, null=True)  # Encrypted TOTP secret
    backup_tokens_count = models.IntegerField(default=0)  # Number of remaining backup codes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'auth_user_two_factor'
        verbose_name = 'User Two Factor'
        verbose_name_plural = 'User Two Factors'
    
    def __str__(self):
        return f"2FA for {self.user.email} ({'Enabled' if self.is_enabled else 'Disabled'})"
    
    @classmethod
    def get_encryption_key(cls):
        """Get or generate encryption key for TOTP secrets."""
        # In production, this should be stored in environment variables
        key = getattr(settings, 'TOTP_ENCRYPTION_KEY', None)
        if not key:
            # Generate a new key if not set (development only)
            key = Fernet.generate_key()
            # Log warning about missing encryption key
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("TOTP_ENCRYPTION_KEY not set in settings. Using generated key (not recommended for production)")
        
        if isinstance(key, str):
            key = key.encode()
        
        return key
    
    def set_secret_key(self, secret_key):
        """Encrypt and store the TOTP secret key."""
        if secret_key:
            fernet = Fernet(self.get_encryption_key())
            encrypted_secret = fernet.encrypt(secret_key.encode())
            self.secret_key_encrypted = base64.b64encode(encrypted_secret).decode()
        else:
            self.secret_key_encrypted = None
    
    def get_secret_key(self):
        """Decrypt and return the TOTP secret key."""
        if not self.secret_key_encrypted:
            return None
        
        try:
            fernet = Fernet(self.get_encryption_key())
            encrypted_secret = base64.b64decode(self.secret_key_encrypted.encode())
            return fernet.decrypt(encrypted_secret).decode()
        except Exception:
            # Log error and return None if decryption fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to decrypt TOTP secret for user {self.user.id}")
            return None
    
    def generate_backup_codes(self, count=10):
        """Generate new backup codes and return them."""
        # Clear existing backup codes
        self.backup_codes.all().delete()
        
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            codes.append(code)
            
            # Create hashed backup code in database
            TwoFactorBackupCode.objects.create(
                user_two_factor=self,
                code_hash=TwoFactorBackupCode.hash_code(code)
            )
        
        self.backup_tokens_count = count
        self.save()
        
        return codes


class TwoFactorBackupCode(models.Model):
    """Model to store hashed backup codes for Two-Factor Authentication recovery."""
    
    user_two_factor = models.ForeignKey(UserTwoFactor, on_delete=models.CASCADE, related_name='backup_codes')
    code_hash = models.CharField(max_length=64)  # SHA-256 hash of the backup code
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'auth_two_factor_backup_code'
        verbose_name = 'Two Factor Backup Code'
        verbose_name_plural = 'Two Factor Backup Codes'
        indexes = [
            models.Index(fields=['code_hash']),
            models.Index(fields=['is_used']),
        ]
    
    def __str__(self):
        status = "Used" if self.is_used else "Available"
        return f"Backup code for {self.user_two_factor.user.email} ({status})"
    
    @staticmethod
    def hash_code(code):
        """Hash a backup code using SHA-256."""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def verify_code(self, code):
        """Verify if the provided code matches this backup code."""
        return not self.is_used and self.code_hash == self.hash_code(code)
    
    def mark_as_used(self):
        """Mark this backup code as used."""
        from django.utils import timezone
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
        
        # Update remaining backup tokens count
        self.user_two_factor.backup_tokens_count = self.user_two_factor.backup_codes.filter(is_used=False).count()
        self.user_two_factor.save()


class TwoFactorAttempt(models.Model):
    """Model to track 2FA verification attempts for rate limiting."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='two_factor_attempts')
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField()
    attempt_type = models.CharField(max_length=20, choices=[
        ('totp', 'TOTP Code'),
        ('backup', 'Backup Code'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_two_factor_attempt'
        verbose_name = 'Two Factor Attempt'
        verbose_name_plural = 'Two Factor Attempts'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"2FA {self.attempt_type} attempt for {self.user.email} ({status})"


class RateLimitConfig(models.Model):
    """Model to store rate limiting configuration."""
    
    name = models.CharField(max_length=100, unique=True, help_text="Configuration name")
    
    # Login rate limits
    login_ip_limit_per_minute = models.IntegerField(default=5, help_text="Max login attempts per IP per minute")
    login_ip_limit_per_hour = models.IntegerField(default=20, help_text="Max login attempts per IP per hour")
    login_ip_limit_per_day = models.IntegerField(default=100, help_text="Max login attempts per IP per day")
    
    login_user_limit_per_minute = models.IntegerField(default=3, help_text="Max login attempts per user per minute")
    login_user_limit_per_hour = models.IntegerField(default=10, help_text="Max login attempts per user per hour")
    login_user_limit_per_day = models.IntegerField(default=50, help_text="Max login attempts per user per day")
    
    # General API rate limits
    api_ip_limit_per_minute = models.IntegerField(default=60, help_text="Max API requests per IP per minute")
    api_ip_limit_per_hour = models.IntegerField(default=1000, help_text="Max API requests per IP per hour")
    
    api_user_limit_per_minute = models.IntegerField(default=100, help_text="Max API requests per user per minute")
    api_user_limit_per_hour = models.IntegerField(default=2000, help_text="Max API requests per user per hour")
    
    # Lockout settings
    ip_lockout_duration = models.IntegerField(default=900, help_text="IP lockout duration in seconds (15 minutes)")
    user_lockout_duration = models.IntegerField(default=600, help_text="User lockout duration in seconds (10 minutes)")
    
    # Advanced settings
    enable_progressive_delays = models.BooleanField(default=True, help_text="Enable progressive delay increases")
    suspicious_activity_threshold = models.IntegerField(default=3, help_text="Failed attempts before marking as suspicious")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_rate_limit_config'
        verbose_name = 'Rate Limit Configuration'
        verbose_name_plural = 'Rate Limit Configurations'
    
    def __str__(self):
        return f"Rate Limit Config: {self.name}"


class VisitorLog(models.Model):
    """Model to log visitor activity for security monitoring."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='visitor_logs')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    
    request_path = models.CharField(max_length=500)
    request_method = models.CharField(max_length=10)
    
    # Authentication info
    is_authenticated = models.BooleanField(default=False)
    username_attempted = models.CharField(max_length=150, blank=True, null=True)
    
    # Response info
    status_code = models.IntegerField(null=True, blank=True)
    is_suspicious = models.BooleanField(default=False)
    
    # Timing
    timestamp = models.DateTimeField(default=timezone.now)
    unix_timestamp = models.BigIntegerField(default=0)
    
    # Geolocation (optional)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'auth_visitor_log'
        verbose_name = 'Visitor Log'
        verbose_name_plural = 'Visitor Logs'
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['session_key', 'timestamp']),
            models.Index(fields=['request_path', 'timestamp']),
            models.Index(fields=['is_suspicious']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.unix_timestamp:
            self.unix_timestamp = int(time.time())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.ip_address} - {self.request_path} - {self.timestamp}"


class IPBlockRule(models.Model):
    """Model to define IP blocking rules."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Rule conditions
    request_path_pattern = models.CharField(max_length=500, blank=True, null=True, 
                                          help_text="URL pattern to match (regex supported)")
    max_attempts = models.IntegerField(default=10, help_text="Max attempts before blocking")
    time_window = models.IntegerField(default=300, help_text="Time window in seconds")
    
    # Block settings
    block_duration = models.IntegerField(default=3600, help_text="Block duration in seconds")
    is_permanent_block = models.BooleanField(default=False)
    
    # Notification settings
    send_alert = models.BooleanField(default=True)
    alert_email = models.EmailField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_ip_block_rule'
        verbose_name = 'IP Block Rule'
        verbose_name_plural = 'IP Block Rules'
    
    def __str__(self):
        return f"IP Block Rule: {self.name}"


class BlockedIP(models.Model):
    """Model to track blocked IPs."""
    
    ip_address = models.GenericIPAddressField(unique=True)
    rule = models.ForeignKey(IPBlockRule, on_delete=models.CASCADE, null=True, blank=True)
    
    # Block info
    reason = models.CharField(max_length=200)
    blocked_at = models.DateTimeField(default=timezone.now)
    block_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    attempt_count = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_permanent = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Admin actions
    blocked_by_admin = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'auth_blocked_ip'
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'
        indexes = [
            models.Index(fields=['ip_address', 'is_active']),
            models.Index(fields=['block_expires_at']),
        ]
    
    def is_blocked(self):
        """Check if IP is currently blocked."""
        if not self.is_active:
            return False
        
        if self.is_permanent:
            return True
        
        if self.block_expires_at and timezone.now() > self.block_expires_at:
            # Block has expired
            self.is_active = False
            self.save()
            return False
        
        return True
    
    def __str__(self):
        status = "Permanently" if self.is_permanent else f"Until {self.block_expires_at}"
        return f"Blocked IP: {self.ip_address} ({status})"
