from rest_framework import serializers
from web_backend.models import Product, ProductAd, ProductRecommendation, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'comment', 'rating', 'created_at']
class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = ['user', 'description']  

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
        fields = ['name', 'price', 'category', 'description', 'seller', 'image_url', 'video_url' 'quantity', 'recommendations', 'ads', 'comments']

class CRUDProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'