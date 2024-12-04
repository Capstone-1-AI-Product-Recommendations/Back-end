# from rest_framework import serializers
# from web_backend.models import Payment, Order


# class PaymentSerializer(serializers.ModelSerializer):
#     order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())  # Link payment to an order
#     payment_method = serializers.CharField(
#         max_length=100)  # Add a field for payment method (e.g., 'Credit Card', 'PayPal')
#     amount = serializers.DecimalField(max_digits=10, decimal_places=2)  # Amount paid
#     payment_status = serializers.CharField(max_length=50)  # Payment status (e.g., 'Completed', 'Pending')
#     payment_date = serializers.DateTimeField()  # Date and time when payment was made

#     class Meta:
#         model = Payment
#         fields = ['payment_id', 'order_id', 'payment_method', 'amount', 'payment_status', 'payment_date', 'created_at',
#                   'updated_at']
#         read_only_fields = ['payment_id', 'created_at', 'updated_at']


# class OrderSerializer(serializers.ModelSerializer):
#     total = serializers.DecimalField(max_digits=10,
#                                      decimal_places=2)  # Assuming `total` is the total price of the order
#     payment_info = PaymentSerializer(read_only=True)  # Nested Payment info, read-only because payment already exists

#     class Meta:
#         model = Order
#         fields = ['order_id', 'user', 'total', 'status', 'created_at', 'updated_at', 'payment_info']
#         read_only_fields = ['order_id', 'created_at', 'updated_at']

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

