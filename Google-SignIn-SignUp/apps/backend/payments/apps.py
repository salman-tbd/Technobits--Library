"""
Payment App Configuration
"""
from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    verbose_name = 'Payment Management'
    
    def ready(self):
        """App ready signal"""
        # Import any signal handlers here if needed
        pass
