from rest_framework import serializers
from .models import Product, Category, Comment

# Serializer cho Product
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'product_id',
            'name',
            'description',
            'price',
            'category',
            'is_featured',
            'created_at',
            'updated_at',
            'seller',
            'address',
            'color',
            'brand',
            'stock_status',
            'discount',  # Thêm discount
            'rating'     # Thêm rating
        ]

# Serializer cho Category
class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)  # Danh sách sản phẩm thuộc danh mục

    class Meta:
        model = Category
        fields = [
            'category_id',
            'category_name',
            'description',
            'products'
        ]

# Serializer cho Comment
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'comment_id',
            'user',
            'product',
            'comment',
            'rating',
            'created_at'
        ]
