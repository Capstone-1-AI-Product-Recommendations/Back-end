# seller_dashboard/serializers.py

from rest_framework import serializers
# from .models import Ad, AdView, ProductAd
from products.serializers import ProductSerializer  # Import ProductSerializer cho việc hiển thị thông tin sản phẩm
from web_backend.models import ShopInfo, Product, Order, OrderItem, Ad, ProductAd, Notification, Comment, ProductRecommendation, Shop

from admin_dashboard.serializers import NotificationSerializer  # Import đúng từ admin_dashboard

# from .models import Ad, AdView, Shop, ShopInfo, SellerProfile
# from products.models import ProductAd
from web_backend.models import *
from products.serializers import ProductSerializer, CommentSerializer
from users.serializers import UserSerializer
from recommendations.serializers import ProductRecommendationSerializer

# AdView Serializer
# class AdViewSerializer(serializers.ModelSerializer):
#     user = UserSerializer()  # Serialize user object as well, if needed
#     ad = AdSerializer()  # Serialize the Ad object
#
#     class Meta:
#         model = AdView
#         fields = ['ad_view_id', 'user', 'ad', 'viewed_at']
#         # Ensure fields match the AdView model

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'
        
# ProductAd Serializer
class ProductAdSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Serialize Product through ProductSerializer
    ad = AdSerializer()  # Serialize the Ad object associated with the ProductAd
    comments = CommentSerializer(source='product.comment_set', many=True, read_only=True)  # Import đúng serializer

    class Meta:
        model = ProductAd
        fields = ['product_ad_id', 'ad', 'product', 'comments', 'created_at', 'updated_at']
        # Ensure fields match the ProductAd model

class ShopSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Serialize User related to the Shop

    class Meta:
        model = Shop
        fields = ['shop_id', 'shop_name', 'user']
        # Ensure fields match the Shop model

# ShopInfo Serializer
class ShopInfoSerializer(serializers.ModelSerializer):
    shop = ShopSerializer()  # Serialize the Shop information
    # Optionally, you could serialize user-related fields here as well

    class Meta:
        model = ShopInfo
        fields = ['shop_info_id', 'shop', 'product_count', 'followers_count', 'is_following', 'join_date']
        # Ensure fields match the ShopInfo model

# SellerProfile Serializer
class SellerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Serialize User associated with the seller profile

    class Meta:
        model = SellerProfile
        fields = ['seller_id', 'store_name', 'store_address', 'user']
        # Ensure fields match the SellerProfile model

    def get_product(self, obj):
        # Trả về thông tin sản phẩm qua ProductSerializer
        return ProductSerializer(obj.product).data

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = '__all__'
class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['shop_name']
    
    def validate_shop_name(self, value):
        if not value:
            raise serializers.ValidationError("Shop name is required.")
        return value
        
class ShopInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopInfo
        fields = ['shop_info_id', 'product_count', 'followers_count', 'is_following', 'join_date']
