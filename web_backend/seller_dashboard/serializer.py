from rest_framework import serializers
from web_backend.models import Order, Comment, Ad, Product

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'user', 'total', 'status', 'created_at', 'updated_at']

class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=50)

class CouponSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    start_date = serializers.DateField()
    end_date = serializers.DateField()

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_id', 'user', 'product', 'comment', 'rating', 'created_at']
