from django.contrib import admin
from .models import PaymentGateway, PaymentTransaction

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ['name', 'gateway_name', 'is_active','test_mode', 'created_at']
    list_filter = ['is_active', 'gateway_name']
    search_fields = ['name', 'merchant_id']
    list_editable = ['is_active','test_mode']

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['gateway', 'amount', 'status', 'created_at']
    list_filter = ['status', 'gateway']
