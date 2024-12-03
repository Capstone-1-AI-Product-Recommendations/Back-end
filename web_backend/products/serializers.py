from rest_framework import serializers
from .models import Product, Category, Comment
from web_backend.models import Product, ProductRecommendation, ProductAd, Comment, ProductImage, ProductVideo, User
from cloudinary.uploader import upload as cloudinary_upload
from cloudinary.uploader import upload
from web_backend.utils import compress_and_upload_image, compress_and_upload_video
import requests
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
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

class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = ['user', 'description']
class ProductAdSerializer(serializers.ModelSerializer):
    ad_title = serializers.CharField(source='ad.title', read_only=True)
    class Meta:
        model = ProductAd
        fields = ['ad_title']  
class DetailCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'comment', 'rating', 'created_at']
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
    seller = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    videos = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'description', 'seller', 'quantity', 'images', 'videos']

    def validate(self, attrs):
        seller = attrs.get('seller')
        if seller.role.role_name != "Seller":
            raise serializers.ValidationError("Only sellers can create products.")
        return attrs
    
    def create(self, validated_data):
        # Lấy dữ liệu ảnh và video từ validated_data
        images_data = validated_data.pop('images', [])
        videos_data = validated_data.pop('videos', [])

        # Tạo sản phẩm mới
        product = Product.objects.create(**validated_data)

        # Xử lý ảnh
        if images_data:
            for image_data in images_data:
                # Tải ảnh lên Cloudinary
                image_url = compress_and_upload_image(image_data)
                # upload_result = cloudinary_upload(image_data)
                # image_url = upload_result.get('secure_url')  # Lấy URL của ảnh từ Cloudinary
                # Lưu URL ảnh vào bảng ProductImage
                ProductImage.objects.create(product=product, file=image_url)

        # Xử lý video
        if videos_data:
            for video_data in videos_data:
                # Tải video lên Cloudinary
                video_url = compress_and_upload_video(video_data)
                # upload_result = cloudinary_upload(video_data)
                # video_url = upload_result.get('secure_url')  # Lấy URL của video từ Cloudinary
                # Lưu URL video vào bảng ProductVideo
                ProductVideo.objects.create(product=product, file=video_url)

        return product
