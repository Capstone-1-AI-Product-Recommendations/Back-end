# seller_dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('ads/', views.get_ads, name='ads'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
]
