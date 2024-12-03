# recommendation/serializers.py
from rest_framework import serializers
# from .models import ProductRecommendation
from web_backend.models import *
from products.serializers import ProductSerializer, CategorySerializer

class ProductRecommendationSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = ProductRecommendation
        fields = ['recommendation_id', 'user', 'product', 'category', 'recommended_at']

    def get_product(self, obj):
        # Check if the product exists and serialize it
        if obj.product:
            return ProductSerializer(obj.product).data
        return None  # If no product exists, return None

    def get_category(self, obj):
        # Check if the category exists and serialize it
        if obj.category:
            return CategorySerializer(obj.category).data
        return None  # If no category exists, return None
