from rest_framework import serializers
from web_backend.models import Cart, CartItem, Product

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