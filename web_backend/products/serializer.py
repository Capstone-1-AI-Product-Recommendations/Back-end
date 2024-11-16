from rest_framework import serializers
from web_backend.models import Product, ProductRecommendation, ProductAd, Comment
import cloudinary.uploader
import tempfile
from io import BytesIO
from moviepy.editor import VideoFileClip
import os
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
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.category_name', allow_null=True)
    seller = serializers.CharField(source='seller.username', read_only=True)
    recommendations = ProductRecommendationSerializer(
        source='productrecommendation_set', many=True, read_only=True
    )
    ads = ProductAdSerializer(source='productad_set', many=True, read_only=True)
    comments = CommentSerializer(source='comment_set', many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            'name', 'price', 'category', 'description', 'seller', 'image_url', 'video_url',
            'quantity', 'recommendations', 'ads', 'comments'
        ]
class CRUDProductSerializer(serializers.ModelSerializer):
    image_file = serializers.ImageField(write_only=True, required=False)
    video_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = [
            'name', 'price', 'category', 'description', 'seller', 'quantity',
            'image_url', 'video_url', 'image_file', 'video_file'
        ]

    def validate_image_file(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image size must be under 10MB.")
        return value

    def validate_video_file(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Video size must be under 10MB.")
        return value

    def compress_image(self, image_file):
        from PIL import Image
        img = Image.open(image_file)
        img = img.convert('RGB')
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)  # Nén chất lượng 85%
        buffer.seek(0)
        return buffer

    def compress_video(self, video_file):
        # Tạo tệp tạm thời để lưu video đã nén
        temp_path = video_file.temporary_file_path()
        temp_video = tempfile.NamedTemporaryFile(delete=False)
        temp_video_path = temp_video.name
        
        clip = VideoFileClip(temp_path)
        # Nén video xuống bitrate thấp
        clip.write_videofile(temp_video_path, bitrate="500k", audio_codec="aac")
        clip.close()

        # Đọc lại video đã nén và đóng tệp tạm thời
        with open(temp_video_path, 'rb') as compressed_video:
            return compressed_video

    def create(self, validated_data):
        image_file = validated_data.pop('image_file', None)
        video_file = validated_data.pop('video_file', None)

        if image_file:
            compressed_image = self.compress_image(image_file)
            upload_result = cloudinary.uploader.upload(compressed_image, resource_type="image")
            validated_data['image_url'] = upload_result['secure_url']

        if video_file:
            compressed_video = self.compress_video(video_file)
            upload_result = cloudinary.uploader.upload(compressed_video, resource_type="video")
            validated_data['video_url'] = upload_result['secure_url']

        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image_file', None)
        video_file = validated_data.pop('video_file', None)

        if image_file:
            compressed_image = self.compress_image(image_file)
            upload_result = cloudinary.uploader.upload(compressed_image, resource_type="image")
            instance.image_url = upload_result['secure_url']

        if video_file:
            compressed_video = self.compress_video(video_file)
            upload_result = cloudinary.uploader.upload(compressed_video, resource_type="video")
            instance.video_url = upload_result['secure_url']

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance