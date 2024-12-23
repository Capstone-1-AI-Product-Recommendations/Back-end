# admin_dashboard/serializers.py
from rest_framework import serializers
# from .models import Notification, UserBrowsingBehavior
# from users.models import User
# from products.models import Product
from web_backend.models import *

class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Chuyển đổi user thành dạng chuỗi nếu cần hiển thị thông tin người dùng.

    class Meta:
        model = Notification
        fields = ['notification_id', 'user', 'message', 'is_read', 'created_at']


class UserBrowsingBehaviorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Chuyển đổi user thành dạng chuỗi nếu cần hiển thị thông tin người dùng.
    product = serializers.StringRelatedField()  # Chuyển đổi product thành dạng chuỗi nếu cần hiển thị thông tin sản phẩm.

    class Meta:
        model = UserBrowsingBehavior
        fields = ['behavior_id', 'user', 'product', 'activity_type', 'interaction_value', 'timestamp']

class CreateUserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(write_only=True)
    role = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'full_name', 'created_at', 'updated_at', 'password', 'phone_number', 'role_name', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        role_name = validated_data.pop('role_name', None)
        user = super().create(validated_data)
        if role_name:
            role_instance, created = Role.objects.get_or_create(role_name=role_name)
            user.role = role_instance
            user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.shop_name', read_only=True)
    images = serializers.StringRelatedField(many=True)

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'images', 'quantity', 'price', 'shop_name', 'created_at']
