from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'user', 'status', 'total', 'created_at', 'updated_at']  # Cập nhật các trường cho phù hợp với model Order

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'order', 'product', 'quantity', 'price']  # Cập nhật các trường cho phù hợp với model OrderItem

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['cart_id', 'user', 'created_at', 'updated_at']  # Cập nhật các trường cho phù hợp với model Cart

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['cart_item_id', 'cart', 'product', 'quantity', 'added_at']  # Cập nhật các trường cho phù hợp với model CartItem
