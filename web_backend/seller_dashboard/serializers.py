# seller_dashboard/serializers.py
from rest_framework import serializers
from .models import Ad, AdView, ProductAd
from products.serializers import ProductSerializer  # Import ProductSerializer cho việc hiển thị thông tin sản phẩm

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['ad_id', 'title', 'description', 'discount_percentage', 'start_date', 'end_date', 'created_at', 'updated_at']
        # Cập nhật các trường cho phù hợp với model Ad

class AdViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdView
        fields = ['ad_view_id', 'user', 'ad', 'viewed_at']
        # Cập nhật các trường cho phù hợp với model AdView

class ProductAdSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = ProductAd
        fields = ['product_ad_id', 'ad', 'product', 'created_at', 'updated_at']
        # Cập nhật các trường cho phù hợp với model ProductAd

    def get_product(self, obj):
        # Trả về thông tin sản phẩm qua ProductSerializer
        return ProductSerializer(obj.product).data
