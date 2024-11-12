# admin_dashboard/views.py
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Notification, UserBrowsingBehavior
from seller_dashboard.models import Ad
from users.models import User
from .serializers import NotificationSerializer, UserBrowsingBehaviorSerializer
from users.serializers import UserSerializer
from seller_dashboard.serializers import AdSerializer
from users.decorators import admin_required

# Hiển thị thông báo vào trang admin_dashboard
@admin_required
def admin_dashboard(request):
    return JsonResponse({"message": "Welcome to Admin Dashboard"})

# API danh sách người dùng
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()
