from rest_framework import serializers
# from .models import Order, OrderItem, Product, UserBankAccount
from web_backend.models import Order, OrderItem, ShippingAddress
# from .models import Order, OrderItem, Cart, CartItem

# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = ['order_id', 'user', 'status', 'total', 'created_at', 'updated_at']  # Cập nhật các trường cho phù hợp với model Order

# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ['order_item_id', 'order', 'product', 'quantity', 'price']  # Cập nhật các trường cho phù hợp với model OrderItem

# class CartSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Cart
#         fields = ['cart_id', 'user', 'created_at', 'updated_at']  # Cập nhật các trường cho phù hợp với model Cart

# class CartItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CartItem
#         fields = ['cart_item_id', 'cart', 'product', 'quantity', 'added_at']  # Cập nhật các trường cho phù hợp với model CartItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'price']

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['recipient_name', 'recipient_phone', 'recipient_address']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'total', 'status', 'order_items', 'shipping_address']