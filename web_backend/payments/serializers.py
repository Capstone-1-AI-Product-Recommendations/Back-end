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