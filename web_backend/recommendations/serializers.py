# recommendations/serializers.py
from rest_framework import serializers
from .models import ProductRecommendation
from products.serializers import ProductSerializer, CategorySerializer

class ProductRecommendationSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = ProductRecommendation
        fields = ['recommendation_id', 'user', 'product', 'category', 'recommended_at']

    def get_product(self, obj):
        return ProductSerializer(obj.product).data

    def get_category(self, obj):
        return CategorySerializer(obj.category).data if obj.category else None
