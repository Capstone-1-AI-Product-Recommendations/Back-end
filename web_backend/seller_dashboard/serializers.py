# seller_dashboard/serializers.py
from rest_framework import serializers
# from .models import Ad, AdView, ProductAd
from products.serializers import ProductSerializer  # Import ProductSerializer cho việc hiển thị thông tin sản phẩm
from web_backend.models import ShopInfo, Product, Order, OrderItem, Ad, ProductAd, Notification, Comment, ProductRecommendation, Shop

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['ad_id', 'title', 'description', 'discount_percentage', 'start_date', 'end_date', 'created_at', 'updated_at']
        # Cập nhật các trường cho phù hợp với model Ad

# class AdViewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdView
#         fields = ['ad_view_id', 'user', 'ad', 'viewed_at']
#         # Cập nhật các trường cho phù hợp với model AdView

class ProductAdSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = ProductAd
        fields = ['product_ad_id', 'ad', 'product', 'created_at', 'updated_at']
        # Cập nhật các trường cho phù hợp với model ProductAd

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

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'

class ProductAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAd
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