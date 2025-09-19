from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    verbose_name = 'Stripe Payments'
    
    def ready(self):
        """Initialize Stripe configuration when app is ready."""
        try:
            import stripe
            from django.conf import settings
            
            # Set Stripe API key
            if hasattr(settings, 'STRIPE_SECRET_KEY') and settings.STRIPE_SECRET_KEY:
                stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Import signals
            from . import signals
        except ImportError:
            # Stripe not installed yet
            pass
