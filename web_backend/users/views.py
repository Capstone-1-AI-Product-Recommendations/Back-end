from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from .decorators import admin_required
from .models import User, Role
from .serializers import UserSerializer

# Create your views here.

# Admin có thể thay đổi role của người dùng thành "seller" hoặc ngược lại.
class AdminUserRoleUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, user_id):
        try:
            # Tìm người dùng cần cập nhật
            user = User.objects.get(user_id=user_id)
            # Kiểm tra Role
            role_id = request.data.get('role_id')

            if not role_id:
                return Response({'error': 'Role ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            # Tìm kiếm Role
            try:
                role = Role.objects.get(role_id=role_id)
            except Role.DoesNotExist:
                return Response({'error': 'Invalid Role ID'}, status=status.HTTP_404_NOT_FOUND)
            # Cập nhật vai trò người dùng
            user.role = role
            user.save()
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
