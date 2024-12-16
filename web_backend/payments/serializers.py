# payments/serializers.py
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
from web_backend.models import Payment, Order, OrderItem, ShippingAddress, Payment, Product

       
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
    order_id = serializers.IntegerField(required=True)  # Truyền order_id từ client
    payment_method = serializers.CharField(max_length=50, required=True)

    class Meta:
        model = Payment
        fields = ['order_id', 'payment_method', 'amount', 'status', 'transaction_id']

    def validate_order_id(self, value):
        try:
            # Kiểm tra Order có tồn tại không
            order = Order.objects.get(pk=value)
            if order.status != "Pending":  # Ví dụ kiểm tra trạng thái order
                raise serializers.ValidationError("Order must be in Pending status.")
            return order
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")

    def create(self, validated_data):
        order = validated_data.pop('order_id')
        # Lấy thông tin khác từ order
        user = order.user
        amount = order.total

        # Tạo Payment
        payment = Payment.objects.create(
            order=order,
            user=user,
            amount=amount,
            status="Pending",
            payment_method=validated_data.get('payment_method'),
            transaction_id=validated_data.get('transaction_id', ""),  # Optional
        )
        return payment
class OrderCODResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    payment_status = serializers.CharField()
    payment_method = serializers.CharField()
    total_amount = serializers.CharField()
    user_name = serializers.CharField()
    shipping_address = ShippingAddressSerializer()
    items = OrderItemSerializer(many=True)
