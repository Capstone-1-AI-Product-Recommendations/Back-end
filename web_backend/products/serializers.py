from rest_framework import serializers
from .models import Product, Category, Comment
from web_backend.models import Product, ProductRecommendation, ProductAd, Comment, ProductImage, ProductVideo, User
from cloudinary.uploader import upload as cloudinary_upload
from web_backend.utils import compress_and_upload_image, compress_and_upload_video
import requests
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status
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
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'comment', 'rating', 'created_at']
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['file']
class ProductVideoSerializer(serializers.ModelSerializer):
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
    comments = CommentSerializer(source='comment_set', many=True, read_only=True)
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
        images = validated_data.pop('images', [])
        videos = validated_data.pop('videos', [])
        product = super().create(validated_data)

        # Upload images
        for image in images:
            image_url = compress_and_upload_image(image)
            product.images.create(file=image_url)

        # Upload videos
        for video in videos:
            video_url = compress_and_upload_video(video)
            product.videos.create(file=video_url)

        return product

    def update(self, instance, validated_data):
        images = validated_data.pop('images', [])
        videos = validated_data.pop('videos', [])

        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Xử lý ảnh và upload lên Cloudinary
        if images:
            instance.images.all().delete()  # Xóa các ảnh cũ
            for image in images:
                try:
                    compressed_image = compress_and_upload_image(image)
                    cloudinary_response = cloudinary_upload(compressed_image, folder='products/images/')
                    ProductImage.objects.create(product=instance, file=cloudinary_response['secure_url'])
                except Exception as e:
                    return Response({"detail": f"Error uploading image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Xử lý video và upload lên Cloudinary
        if videos:
            instance.videos.all().delete()  # Xóa các video cũ
            for video in videos:
                try:
                    compressed_video = compress_and_upload_video(video)
                    cloudinary_response = cloudinary_upload(compressed_video, resource_type="video", folder='products/videos/')
                    ProductVideo.objects.create(product=instance, file=cloudinary_response['secure_url'])
                except Exception as e:
                    return Response({"detail": f"Error uploading video: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return instance