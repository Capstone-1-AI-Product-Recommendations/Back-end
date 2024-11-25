# seller_dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('ads/', views.get_ads, name='ads'), # API lấy danh sách quảng cáo
    path('ads/create/', views.create_ad, name='create_ad'),  # API tạo quảng cáo
    path('ads/homepage-banners/', views.get_homepage_banners, name='get_homepage_banners'),  # API quảng cáo homepage
]
