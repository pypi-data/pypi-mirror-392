from rest_framework import serializers
from .models import PaymentGateway, PaymentTransaction

class PaymentGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGateway
        fields = ['id','name', 'gateway_name', 'is_active', 'priority']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            'user_token',
            'amount',
            'status',
            'gateway',
        ]
        read_only_fields = fields
