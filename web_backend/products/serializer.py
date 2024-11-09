from rest_framework import serializers
from web_backend.models import Product, ProductAd, ProductRecommendation

class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = ['user']  

class ProductAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAd
        fields = ['ad_title']  

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.category_name', allow_null=True)
    recommendations = ProductRecommendationSerializer(many=True, read_only=True)
    ads = ProductAdSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'description', 'seller', 'video', 'image' 'quantity', 'recommendations', 'ads']

class CRUDProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'