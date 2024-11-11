# admin_dashboard/views.py
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Notification, UserBrowsingBehavior
from seller_dashboard.models import Ad
from users.models import User
from .serializers import NotificationSerializer, UserBrowsingBehaviorSerializer
from seller_dashboard.serializers import AdSerializer
from users.decorators import admin_required

# Create your views here.

@admin_required
def admin_dashboard(request):
    return JsonResponse({"message": "Welcome to Admin Dashboard"})

