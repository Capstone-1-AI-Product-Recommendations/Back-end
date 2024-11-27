# admin_dashboard/serializers.py
from rest_framework import serializers
from .models import Notification, UserBrowsingBehavior
from users.models import User
from products.models import Product

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['notification_id', 'user', 'message', 'is_read', 'created_at']

class UserBrowsingBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBrowsingBehavior
        fields = ['behavior_id', 'user', 'product', 'activity_type', 'interaction_value', 'timestamp']