# views.py của app products
from django.shortcuts import render
from .models import *
from .serializers import ProductSerializer, CommentSerializer, CategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
# Create your views here.

@api_view(['GET'])
def get_featured_products(request):
    featured_products = Product.objects.filter(is_featured=True)
    serialized_data = ProductSerializer(featured_products, many=True).data
    return Response(serialized_data)

@api_view(['GET'])
def get_trending_products(request):
    trending_products = Product.objects.annotate(
        total_views=Count('userbrowsingbehavior__product')
    ).order_by('-total_views')[:5]
    serialized_data = ProductSerializer(trending_products, many=True).data
    return Response(serialized_data)

@api_view(['GET'])
def get_popular_categories(request):
    popular_categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('-product_count')[:3]
    serialized_data = CategorySerializer(popular_categories, many=True).data
    return Response(serialized_data)

@api_view(['GET'])
def get_all_categories(request):
    all_categories = Category.objects.all()
    serialized_data = CategorySerializer(all_categories, many=True).data
    return Response(serialized_data)

@api_view(['GET'])
def get_latest_comments(request):
    latest_comments = Comment.objects.order_by('-created_at')[:3]
    serialized_data = CommentSerializer(latest_comments, many=True).data
    return Response(serialized_data)



#Tổng hợp API cho homepage
# main_app/views.py

import requests

@api_view(['GET'])
def homepage_api(request):
    # Gọi các API con để lấy dữ liệu
    featured_products = requests.get('http://localhost:8000/products/featured/').json()
    trending_products = requests.get('http://localhost:8000/products/trending/').json()
    recommended_products = requests.get('http://localhost:8000/recommendations/recommended/').json() if request.user.is_authenticated else []
    popular_categories = requests.get('http://localhost:8000/products/popular-categories/').json()
    latest_comments = requests.get('http://localhost:8000/products/latest-comments/').json()
    ads = requests.get('http://localhost:8000/seller_dashboard/ads/').json()
    all_categories = requests.get('http://localhost:8000/products/all-categories/').json()

    # Tổng hợp dữ liệu
    data = {
        'featured_products': featured_products,
        'trending_products': trending_products,
        'recommended_products': recommended_products,
        'popular_categories': popular_categories,
        'latest_comments': latest_comments,
        'ads': ads,
        'all_categories': all_categories,
    }
    return Response(data)
