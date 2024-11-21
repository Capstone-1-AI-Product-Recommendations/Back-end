from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from web_backend.models import Order, Comment, Ad
from .serializer import OrderSerializer, OrderStatusUpdateSerializer, CouponSerializer, ReviewSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Chỉ cho phép user đã đăng nhập
def order_list(request):
    seller = request.user
    if not seller.is_authenticated:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

    orders = Order.objects.filter(orderitem__product__seller=seller).distinct()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_order_status(request, order_id):
    seller = request.user
    order = get_object_or_404(Order, pk=order_id, orderitem__product__seller=seller)

    serializer = OrderStatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        order.status = serializer.validated_data['status']
        order.save()
        return Response({"message": "Order status updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_coupon(request):
    serializer = CouponSerializer(data=request.data)
    if serializer.is_valid():
        # Lưu coupon
        coupon = Ad.objects.create(**serializer.validated_data)
        return Response({"message": "Coupon created successfully.", "coupon_id": coupon.ad_id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def review_list(request):
    seller = request.user
    reviews = Comment.objects.filter(product__seller=seller)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)