# admin_dashboard/urls.py
from django.urls import path
from . import views
from .views import admin_dashboard, UserListView

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('users/', UserListView.as_view(), name='user-list'),
]
