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
