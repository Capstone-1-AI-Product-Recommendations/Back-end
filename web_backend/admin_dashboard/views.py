# admin_dashboard/views.py
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.db.models import Q
from .models import Notification, UserBrowsingBehavior
from seller_dashboard.models import Ad
from users.models import User
from products.models import Category
from orders.models import Order
from .serializers import NotificationSerializer, UserBrowsingBehaviorSerializer
from users.serializers import UserSerializer
from products.serializers import CategorySerializer
from orders.serializers import OrderSerializer
from seller_dashboard.serializers import AdSerializer
from users.decorators import admin_required

# API để lấy danh sách người dùng (GET)
@api_view(['GET'])
@admin_required
def get_users(request):
    users = User.objects.all()
    serialized_data = UserSerializer(users, many=True).data
    return Response(serialized_data)

# API để thêm người dùng mới (POST)
@api_view(['POST'])
@admin_required
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API để lấy thông tin chi tiết của một người dùng (GET)
@api_view(['GET'])
@admin_required
def get_user_detail(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        serialized_data = UserSerializer(user).data
        return Response(serialized_data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# API để cập nhật thông tin người dùng (PUT)
@api_view(['PUT'])
@admin_required
def update_user(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# API để xóa người dùng (DELETE)
@api_view(['DELETE'])
@admin_required
def delete_user(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# API để tìm kiếm người dùng dựa trên username, email hoặc role.
@api_view(['GET'])
@admin_required
def search_users(request):
    query = request.query_params.get('query', '').strip()
    if not query:
        return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)

    users = User.objects.filter(
        Q(username__icontains=query) |  # Tìm kiếm theo username
        Q(email__icontains=query) |    # Tìm kiếm theo email
        Q(role__role_name__icontains=query)  # Tìm kiếm theo tên vai trò
    ).distinct()

    if users.exists():
        serialized_data = UserSerializer(users, many=True).data
        return Response(serialized_data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'No users found matching the query'}, status=status.HTTP_404_NOT_FOUND)

# API xem danh sách người dùng theo role
@api_view(['GET'])
@admin_required
def get_users_by_role(request, role_name):
    try:
        users = User.objects.filter(role__role_name=role_name)
        serialized_data = UserSerializer(users, many=True).data
        return Response(serialized_data, status=status.HTTP_200_OK)
    except Role.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

# API check trang thái của người dùng
@api_view(['GET'])
@admin_required
def check_user_active_status(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        return Response({
            'user_id': user.user_id,
            'username': user.username,
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# API active / ban tài khoản người dùng
@api_view(['PUT'])
@admin_required
def toggle_user_active_status(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        user.is_active = not user.is_active
        user.save()
        return Response({
            'message': f"User {'activated' if user.is_active else 'deactivated'} successfully.",
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# API Tạo Thông Báo Cho Người Dùng
@api_view(['POST'])
@admin_required
def send_notification(request):
    user_id = request.data.get('user_id')
    message = request.data.get('message')

    if not message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

    if user_id == 'all':
        users = User.objects.all()
    else:
        try:
            users = [User.objects.get(user_id=user_id)]
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    for user in users:
        Notification.objects.create(user=user, message=message, is_read=0)

    return Response({'message': 'Notification(s) sent successfully'}, status=status.HTTP_201_CREATED)

# API Xem Lịch Sử Thông Báo Được Gửi
@api_view(['GET'])
@admin_required
def get_notification_history(request, user_id=None):
    if user_id:
        notifications = Notification.objects.filter(user_id=user_id)
    else:
        notifications = Notification.objects.all()

    serialized_data = NotificationSerializer(notifications, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API Tạo một danh mục sản phẩm mới
@api_view(['POST'])
@admin_required
def create_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API Cập nhật danh mục sản phẩm
@api_view(['PUT'])
@admin_required
def update_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategorySerializer(category, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API Xóa danh 1 danh mục sản phẩm
@api_view(['DELETE'])
@admin_required
def delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        category.delete()
        return Response({'message': 'Category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

# API Lấy danh sách đơn hàng
@api_view(['GET'])
@admin_required
def get_orders(request):
    orders = Order.objects.all().order_by('-created_at')  # Sắp xếp theo ngày tạo
    serialized_data = OrderSerializer(orders, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API Tìm kiếm đơn hàng
@api_view(['GET'])
@admin_required
def search_orders(request):
    query = request.query_params.get('query', '').strip()

    if not query:
        return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Tìm kiếm theo ID đơn hàng, username người dùng, hoặc trạng thái đơn hàng
    orders = Order.objects.filter(
        Q(order_id__icontains=query) |
        Q(user__username__icontains=query) |
        Q(status__icontains=query)
    ).distinct().order_by('-created_at')

    if orders.exists():
        serialized_data = OrderSerializer(orders, many=True).data
        return Response(serialized_data, status=status.HTTP_200_OK)

    return Response({'message': 'No orders found matching the query'}, status=status.HTTP_404_NOT_FOUND)
