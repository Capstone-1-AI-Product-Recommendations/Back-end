# cart/serializers.py
from rest_framework import serializers
# from carts.models import Cart, CartItem  # Import các model trong app carts
# from products.models import Product  # Giả sử bạn có model Product trong app products
from web_backend.models import *

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')  # Trích xuất tên sản phẩm từ product
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)  # Trích xuất giá sản phẩm từ product

    class Meta:
        model = CartItem
        fields = ['product_name', 'product_price', 'quantity', 'cart_item_id']  # Các trường cần thiết cho CartItem


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True)  # Sử dụng CartItemSerializer để hiển thị các mục trong giỏ hàng
    total = serializers.SerializerMethodField()  # Trường tổng giá trị của giỏ hàng

    class Meta:
        model = Cart
        fields = ['user', 'items', 'total']  # Các trường cần thiết cho Cart

    def get_total(self, cart):
        # Tính tổng giá trị giỏ hàng (tính từ các CartItem)
        total = sum(item.product.price * item.quantity for item in cart.cartitem_set.all())
        return total



class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)

    class Meta:
        model = CartItem
        fields = ['product_name', 'product_price', 'quantity', 'cart_item_id']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['user', 'items', 'total']

    def get_total(self, cart):
        total = sum(item.product.price * item.quantity for item in cart.cartitem_set.all())
        return total
