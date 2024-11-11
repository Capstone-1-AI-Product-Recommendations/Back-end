# admin_dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin-dashboard'),
]
