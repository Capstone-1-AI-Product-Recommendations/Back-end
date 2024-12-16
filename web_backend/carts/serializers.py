# cart/serializers.py
from rest_framework import serializers
from web_backend.models import Cart, CartItem, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['file']

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')  # Trích xuất tên sản phẩm từ product
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)  # Trích xuất giá sản phẩm từ product
    product_images = ProductImageSerializer(source='product.images', many=True)
    shop_name = serializers.CharField(source='product.shop.shop_name')  # Trích xuất tên shop từ product

    class Meta:
        model = CartItem
        fields = ['product_name', 'product_price', 'quantity', 'cart_item_id', 'product_images', 'shop_name']  # Các trường cần thiết cho CartItem

class ShopCartSerializer(serializers.Serializer):
    shop_name = serializers.CharField()
    items = CartItemSerializer(many=True)

class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['user', 'items']

    def get_items(self, obj):
        cart_items = obj.cartitem_set.all()
        shop_dict = {}
        for item in cart_items:
            shop_name = item.product.shop.shop_name
            if shop_name not in shop_dict:
                shop_dict[shop_name] = []
            shop_dict[shop_name].append(item)
        
        shop_carts = []
        for shop_name, items in shop_dict.items():
            shop_carts.append({
                'shop_name': shop_name,
                'items': CartItemSerializer(items, many=True).data
            })
        
        return shop_carts
