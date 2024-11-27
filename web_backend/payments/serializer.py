from rest_framework import serializers
from web_backend.models import Payment, Order

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'user', 'total', 'status', 'created_at', 'updated_at']