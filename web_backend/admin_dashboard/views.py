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
from .serializers import NotificationSerializer, UserBrowsingBehaviorSerializer
from users.serializers import UserSerializer
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