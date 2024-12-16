# products/serializers.py
from rest_framework import serializers
from web_backend.models import Product, ProductRecommendation, ProductAd, Comment, ProductImage, ProductVideo, User, Category, Subcategory
from users.serializers import UserSerializer
from cloudinary.uploader import upload as cloudinary_upload
from web_backend.models import Shop, Product, ProductRecommendation, ProductAd, Comment, ProductImage, ProductVideo, User, Category, Subcategory
from users.serializers import UserSerializer
from cloudinary.uploader import upload as cloudinary_upload
from cloudinary.uploader import upload
from web_backend.utils import compress_and_upload_image, compress_and_upload_video
import requests
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

# Serializer for Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'category_name', 'description']


# Serializer for Subcategory
class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    class Meta:
        model = Subcategory
        fields = ['subcategory_id', 'subcategory_name', 'description', 'category_name']


# Serializer for ProductRecommendation
# class ProductRecommendationSerializer(serializers.ModelSerializer):
#     category_name = serializers.CharField(source='category.category_name', read_only=True)

#     class Meta:
#         model = ProductRecommendation
#         fields = ['recommendation_id', 'session_id', 'description', 'recommended_at', 'category_name', 'product']
#         fields = ['subcategory_id', 'subcategory_name', 'category_name', 'description']


# Serializer for ProductRecommendation
class ProductRecommendationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = Subcategory
        fields = ['subcategory_id', 'subcategory_name', 'description', 'category_name']


# Serializer for ProductRecommendation
class ProductRecommendationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = ProductRecommendation
        fields = ['recommendation_id', 'session_id', 'description', 'recommended_at', 'category_name', 'product']


# Serializer for ProductAd
class ProductAdSerializer(serializers.ModelSerializer):
    ad_title = serializers.CharField(source='ad.title', read_only=True)

    class Meta:
        model = ProductAd
        fields = ['product_ad_id', 'ad_title']

# # Serializer for Comment
# class CommentSerializer(serializers.ModelSerializer):
#     user_name = serializers.CharField(source='user.username', read_only=True)
#     created_at = serializers.DateTimeField(read_only=True)

#     class Meta:
#         model = Comment
#         fields = ['comment_id', 'user_name', 'comment', 'rating', 'created_at']

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
        

# class CommentSerializer(serializers.ModelSerializer):
#     user = serializers.CharField(source='user.username', read_only=True)
#     created_at = serializers.DateTimeField(read_only=True)

#     class Meta:
#         model = Comment
#         fields = ['user', 'comment', 'rating', 'created_at']

# Serializer for ProductImage model
class ProductImageSerializer(serializers.ModelSerializer):
    file = serializers.CharField()    
    class Meta:
        model = ProductImage
        fields = ['file']
        
class ProductVideoSerializer(serializers.ModelSerializer):
    file = serializers.CharField()
    class Meta:
        model = ProductVideo
        fields = ['file']


# Serializer for Product
class ProductSerializer(serializers.ModelSerializer):
    # Quan hệ khóa ngoại
    category = CategorySerializer(read_only=True)
    subcategory = SubcategorySerializer(read_only=True)

    # Thông tin seller
    shop_name = serializers.CharField(source='shop.name', read_only=True)  # Thay 'seller.store_name' bằng 'shop.name'

    # Các liên kết nhiều-đến-một
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    comments = CommentSerializer(source='comment_set', many=True, read_only=True)
    ads = ProductAdSerializer(source='productad_set', many=True, read_only=True)
    recommendations = ProductRecommendationSerializer(source='productrecommendation_set', many=True, read_only=True)

    # Các trường tính toán
    rating = serializers.FloatField(read_only=True)  # Thay đổi từ computed_rating thành rating

    # Thêm trường stock_status
    stock_status = serializers.CharField(read_only=True)  # Trường @property trong model

    class Meta:
        model = Product
        fields = [
            'product_id', 'name', 'description', 'price', 'quantity', 'color', 'brand',
            'stock_status', 'category', 'subcategory', 'shop_name',
            'images', 'videos', 'comments', 'ads', 'recommendations',
            'rating', 'sales_strategy'
        ]
        
class DetailCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'comment', 'rating', 'created_at']

class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = ['user', 'description']
class ProductAdSerializer(serializers.ModelSerializer):
    ad_title = serializers.CharField(source='ad.title', read_only=True)
    class Meta:
        model = ProductAd
        fields = ['ad_title']  

class DetailProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.category_name', allow_null=True)
    seller = serializers.CharField(source='seller.username', read_only=True)
    recommendations = ProductRecommendationSerializer(
        source='productrecommendation_set', many=True, read_only=True
    )
    ads = ProductAdSerializer(source='productad_set', many=True, read_only=True)
    comments = DetailCommentSerializer(source='comment_set', many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            'name', 'price', 'category', 'description', 'seller', 'images', 'videos',
            'quantity', 'recommendations', 'ads', 'comments'
        ]

class CRUDProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all(), required=False)
    seller = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    videos = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'subcategory', 'description', 'seller', 'quantity', 'color', 'brand', 'images', 'videos']
        

    # def validate(self, attrs):
    #     seller = attrs.get('seller')
    #     if seller.role.role_name != "Seller":
    #         raise serializers.ValidationError("Only sellers can create products.")
    #     return attrs
    
    def create(self, validated_data):
        category = validated_data.pop('category', None)
        seller = validated_data.pop('seller', None)
        # Lấy dữ liệu ảnh và video từ validated_data
        images_data = validated_data.pop('images', [])
        videos_data = validated_data.pop('videos', [])

        # Tạo sản phẩm mới
        product = Product.objects.create(**validated_data)
        if category:
            product.subcategory = category
            product.save()

        if seller:
            product.User = seller
            product.save()
        # Xử lý ảnh
        if images_data:
            for image_data in images_data:
                # Tải ảnh lên Cloudinary
                image_url = compress_and_upload_image(image_data)
                # upload_result = cloudinary_upload(image_data)
                # image_url = upload_result.get('secure_url')  # Lấy URL của ảnh từ Cloudinary
                # Lưu URL ảnh vào bảng ProductImage
                ProductImage.objects.create(product=product, file=image_url)

        # Nén và lưu video vào Cloudinary
        if videos_data:
            for video_data in videos_data:
                # Tải video lên Cloudinary
                video_url = compress_and_upload_video(video_data)
                # upload_result = cloudinary_upload(video_data)
                # video_url = upload_result.get('secure_url')  # Lấy URL của video từ Cloudinary
                # Lưu URL video vào bảng ProductVideo
                ProductVideo.objects.create(product=product, file=video_url)

        return product
