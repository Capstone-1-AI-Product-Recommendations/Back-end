# orders/serializer.py
from rest_framework import serializers
from web_backend.models import Order, OrderItem, Cart, CartItem, Product

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')  # Show product name in cart item
    product_price = serializers.DecimalField(source='product.price', max_digits=10,
                                             decimal_places=2)  # Show product price

    class Meta:
        model = CartItem
        fields = ['cart_item_id', 'cart', 'product_name', 'product_price', 'quantity', 'added_at']
        read_only_fields = ['cart_item_id', 'added_at']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Assuming 'user' is a foreign key to the User model
    total = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = ['order_id', 'user', 'status', 'total', 'created_at', 'updated_at']
        read_only_fields = ['order_id', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())  # Assuming you link to an Order
    product_name = serializers.CharField(source='product.name')  # To show the product name directly
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)  # Product price

    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'order', 'product_name', 'product_price', 'quantity', 'price']
        read_only_fields = ['order_item_id']


class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Assuming 'user' is a foreign key to the User model
    items = CartItemSerializer(source='cartitem_set', many=True)  # Nested CartItemSerializer for each Cart item

    class Meta:
        model = Cart
        fields = ['cart_id', 'user', 'created_at', 'updated_at', 'items']
        read_only_fields = ['cart_id', 'created_at', 'updated_at']
