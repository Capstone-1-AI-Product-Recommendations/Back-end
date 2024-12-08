from rest_framework import serializers
from web_backend.models import Order, OrderItem, ShippingAddress, Payment, Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'price', 'total_price']
    def get_total_price(self, obj):
        return str(obj.price * obj.quantity)
class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, source='orderitem_set')
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ['user_name', 'total', 'status', 'created_at', 'products']
class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['recipient_name', 'recipient_phone', 'recipient_address']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['status', 'payment_method', 'transaction_id', 'amount']
class OrderCODResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    payment_status = serializers.CharField()
    payment_method = serializers.CharField()
    total_amount = serializers.CharField()
    user_name = serializers.CharField()
    shipping_address = ShippingAddressSerializer()
    items = OrderItemSerializer(many=True)