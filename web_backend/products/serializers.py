from rest_framework import serializers
from web_backend.models import Product, ProductRecommendation, ProductAd, Comment, ProductImage, ProductVideo, User, Category, Subcategory
from users.serializers import UserSerializer
from cloudinary.uploader import upload as cloudinary_upload
from web_backend.utils import compress_and_upload_image, compress_and_upload_video
import requests
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

# Serializer for Category model
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'category_name', 'description']


# Serializer for Subcategory model
class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = Subcategory
        fields = ['subcategory_id', 'subcategory_name', 'category_name', 'description']


# Serializer for ProductRecommendation model
class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = ['user', 'description']


# Serializer for ProductAd model
class ProductAdSerializer(serializers.ModelSerializer):
    ad_title = serializers.CharField(source='ad.title', read_only=True)

    class Meta:
        model = ProductAd
        fields = ['ad_title']


# Serializer for ProductImage model
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['file', 'product']


# Serializer for ProductVideo model
class ProductVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = ['file', 'product']


# Serializer for CRUD Product operations
class CRUDProductSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    subcategory = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all(), required=False)

    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    videos = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'subcategory', 'description', 'seller', 'quantity', 'color', 'brand', 'stock_status', 'images', 'videos']

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
        
class DetailCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'comment', 'rating', 'created_at']
        
# Serializer for Comment model
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

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
    comments = DetailCommentSerializer(source='comment_set', many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            'name', 'price', 'category', 'description', 'seller', 'images', 'videos',
            'quantity', 'recommendations', 'ads', 'comments'
        ]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    subcategory = SubcategorySerializer(read_only=True)
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
            'product_id', 'name', 'price', 'category', 'subcategory', 'description',
            'seller', 'images', 'videos', 'quantity', 'recommendations', 'ads', 'comments',
            'color', 'brand', 'stock_status'
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

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle images and upload to Cloudinary
        if images:
            instance.images.all().delete()  # Delete old images
            for image in images:
                try:
                    compressed_image = compress_and_upload_image(image)
                    cloudinary_response = cloudinary_upload(compressed_image, folder='products/images/')
                    ProductImage.objects.create(product=instance, file=cloudinary_response['secure_url'])
                except Exception as e:
                    raise serializers.ValidationError(f"Error uploading image: {str(e)}")

        # Handle videos and upload to Cloudinary
        if videos:
            instance.videos.all().delete()  # Delete old videos
            for video in videos:
                try:
                    compressed_video = compress_and_upload_video(video)
                    cloudinary_response = cloudinary_upload(compressed_video, resource_type="video", folder='products/videos/')
                    ProductVideo.objects.create(product=instance, file=cloudinary_response['secure_url'])
                except Exception as e:
                    raise serializers.ValidationError(f"Error uploading video: {str(e)}")

        return instance
