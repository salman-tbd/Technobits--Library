from django.contrib import admin
from .models import PaymentTransaction

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['transaction_id', 'google_pay_token']
    readonly_fields = ['transaction_id', 'google_pay_token', 'created_at', 'updated_at']
    ordering = ['-created_at']
