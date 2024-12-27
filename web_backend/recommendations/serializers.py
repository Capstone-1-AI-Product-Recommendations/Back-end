# recommendation/serializers.py
from rest_framework import serializers
# Import models inside functions if necessary to avoid app registry issues
# from web_backend.models import *
from products.serializers import ProductSerializer, CategorySerializer
from web_backend.models import ProductRecommendation, UserBrowsingBehavior, Product

class ProductRecommendationSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = ProductRecommendation
        fields = ['recommendation_id', 'user', 'product', 'category', 'recommended_at']

    def get_product(self, obj):
        # Check if the product exists and serialize it
        if (obj.product):
            return ProductSerializer(obj.product).data
        return None  # If no product exists, return None

    def get_category(self, obj):
        # Check if the category exists and serialize it
        if (obj.category):
            return CategorySerializer(obj.category).data
        return None  # If no category exists, return None

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product  # Set the correct model
        fields = ['product_id', 'name', 'price', 'rating', 'image_url']

    def get_image_url(self, obj):
        # Assuming the Product model has a related name 'images' for ProductImage
        image = obj.images.first()
        return image.file if image else None

class UserBrowsingBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBrowsingBehavior
        fields = '__all__'
