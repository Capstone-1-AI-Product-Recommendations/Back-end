from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from web_backend.models import Product, Order, OrderItem, Ad, ProductAd, SellerProfile, Notification, Comment, ProductRecommendation
from .serializer import ProductSerializer, OrderSerializer, OrderItemSerializer, AdSerializer, ProductAdSerializer, SellerProfileSerializer, NotificationSerializer, CommentSerializer, ProductRecommendationSerializer

# Quản lý đơn hàng
@api_view(['GET'])
def get_orders(request, seller_id):
    orders = Order.objects.filter(orderitem__product__seller_id=seller_id).distinct()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_order_details(request, seller_id, order_id):
    order = get_object_or_404(Order, id=order_id, orderitem__product__seller_id=seller_id)
    order_items = OrderItem.objects.filter(order=order)
    order_item_serializer = OrderItemSerializer(order_items, many=True)
    order_serializer = OrderSerializer(order)
    return Response({
        'order': order_serializer.data,
        'items': order_item_serializer.data
    })

# Quản lý quảng cáo (Ad)
@api_view(['POST'])
def create_ad(request, seller_id):
    serializer = AdSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(seller_id=seller_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_ad(request, seller_id, ad_id):
    ad = get_object_or_404(Ad, id=ad_id, seller_id=seller_id)
    serializer = AdSerializer(ad, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Quản lý hồ sơ seller
@api_view(['GET'])
def get_seller_profile(request, seller_id):
    seller_profile = get_object_or_404(SellerProfile, user_id=seller_id)
    serializer = SellerProfileSerializer(seller_profile)
    return Response(serializer.data)

@api_view(['PUT'])
def update_seller_profile(request, seller_id):
    seller_profile = get_object_or_404(SellerProfile, user_id=seller_id)
    serializer = SellerProfileSerializer(seller_profile, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Quản lý quảng cáo sản phẩm
@api_view(['POST'])
def associate_ad_with_product(request, seller_id):
    serializer = ProductAdSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Thông báo và Quản lý Phản hồi của Người dùng
@api_view(['GET'])
def get_notifications(request, seller_id):
    notifications = Notification.objects.filter(user_id=seller_id)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_comments(request, seller_id):
    comments = Comment.objects.filter(product__seller_id=seller_id)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

# Báo cáo và thống kê
@api_view(['GET'])
def sales_report(request, seller_id):
    orders = Order.objects.filter(orderitem__product__seller_id=seller_id).distinct()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def ad_performance(request, seller_id):
    product_ads = ProductAd.objects.filter(product__seller_id=seller_id)
    serializer = ProductAdSerializer(product_ads, many=True)
    return Response(serializer.data)

# Quản lý khuyến nghị sản phẩm
@api_view(['GET'])
def get_product_recommendations(request, seller_id):
    recommendations = ProductRecommendation.objects.filter(user_id=seller_id)
    serializer = ProductRecommendationSerializer(recommendations, many=True)
    return Response(serializer.data)