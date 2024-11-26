from rest_framework import serializers
from web_backend.models import Product, ProductRecommendation, ProductAd, Comment, ProductImage, ProductVideo
from cloudinary.uploader import upload as cloudinary_upload
from web_backend.utils import compress_and_upload_image, compress_and_upload_video
import requests
from django.core.files.base import ContentFile

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
        fields = ['file', 'uploaded_at']
class ProductVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = ['file', 'uploaded_at']
class ProductSerializer(serializers.ModelSerializer):
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
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    videos = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'description', 'seller', 'quantity', 'images', 'videos']

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
            instance.images.all().delete()
            for image in images:
                compressed_image = compress_and_upload_image(image)
                cloudinary_response = upload(compressed_image, folder='products/images/')
                ProductImage.objects.create(product=instance, file=cloudinary_response['secure_url'])

        # Xử lý video và upload lên Cloudinary
        if videos:
            instance.videos.all().delete()
            for video in videos:
                compressed_video = compress_and_upload_video(video)
                cloudinary_response = upload(compressed_video, resource_type="video", folder='products/videos/')
                ProductVideo.objects.create(product=instance, file=cloudinary_response['secure_url'])

        return instance