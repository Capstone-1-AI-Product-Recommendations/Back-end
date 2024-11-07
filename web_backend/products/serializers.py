# products/serializers.py
from rest_framework import serializers
from .models import Product, Category, Comment

# Serializer cho Product
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'description', 'price', 'category', 'is_featured', 'created_at', 'updated_at', 'seller']  # Sửa 'id' thành 'product_id'

# Serializer cho Category
class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)  # Sử dụng ProductSerializer để lấy danh sách sản phẩm
    class Meta:
        model = Category
        fields = ['category_id', 'category_name', 'description', 'products']  # Sửa 'id' thành 'category_id'

# Serializer cho Comment
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_id', 'user', 'product', 'comment', 'rating', 'created_at']  # Sửa 'id' thành 'comment_id' và thêm trường 'comment'
