# views.py của app products
from django.shortcuts import render
from .models import *
from .serializers import ProductSerializer, CommentSerializer, CategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from django.db.models import Q
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


# ---------------------------------------------------------------------------------------------------------------------
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


#--------------------------------------------------------------------------------------------------------------------
# API con cho bộ lọc theo category
@api_view(['GET'])
def filter_by_category(request):
    category = request.GET.get('category')
    if category:
        products = Product.objects.filter(category__category_name=category)
        products_serialized = ProductSerializer(products, many=True).data
        return Response(products_serialized)
    return Response({"message": "Category parameter is required"}, status=400)

# API con cho bộ lọc theo giá
@api_view(['GET'])
def filter_by_price(request):
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        products = Product.objects.filter(
            Q(price__gte=min_price) & Q(price__lte=max_price)
        )
        products_serialized = ProductSerializer(products, many=True).data
        return Response(products_serialized)
    return Response({"message": "Both min_price and max_price parameters are required"}, status=400)

# API con cho bộ lọc theo màu
@api_view(['GET'])
def filter_by_color(request):
    color = request.GET.get('color')
    if color:
        products = Product.objects.filter(color=color)
        products_serialized = ProductSerializer(products, many=True).data
        return Response(products_serialized)
    return Response({"message": "Color parameter is required"}, status=400)

# API con cho bộ lọc theo brand
@api_view(['GET'])
def filter_by_brand(request):
    brand = request.GET.get('brand')
    if brand:
        products = Product.objects.filter(brand=brand)
        products_serialized = ProductSerializer(products, many=True).data
        return Response(products_serialized)
    return Response({"message": "Brand parameter is required"}, status=400)

# API con cho bộ lọc theo tình trạng kho
@api_view(['GET'])
def filter_by_stock_status(request):
    stock_status = request.GET.get('stock_status')
    if stock_status:
        if stock_status == 'in_stock':
            products = Product.objects.filter(stock_status=Product.IN_STOCK)
        elif stock_status == 'on_sale':
            products = Product.objects.filter(stock_status=Product.ON_SALE)
        else:
            return Response({"message": "Invalid stock_status value"}, status=400)
        products_serialized = ProductSerializer(products, many=True).data
        return Response(products_serialized)
    return Response({"message": "stock_status parameter is required"}, status=400)



# -----------------------------------------------------------------------------------------------------------------
# Tổng hợp API cho Filter_Page
@api_view(['GET'])
def filter_page(request):
    products = Product.objects.all()

    # Filter by category
    category = request.GET.get('category')
    if category:
        products = products.filter(category__category_name=category)

    # Filter by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        products = products.filter(
            Q(price__gte=min_price) & Q(price__lte=max_price)
        )

    # # Filter by color
    # color = request.GET.get('color')
    # if color:
    #     products = products.filter(color=color)
    #
    # # Filter by brand
    # brand = request.GET.get('brand')
    # if brand:
    #     products = products.filter(brand=brand)
    #
    # # Filter by stock status
    # stock_status = request.GET.get('stock_status')
    # if stock_status:
    #     if stock_status == 'in_stock':
    #         products = products.filter(stock_status=Product.IN_STOCK)
    #     elif stock_status == 'on_sale':
    #         products = products.filter(stock_status=Product.ON_SALE)

    # Serialize products for API response
    products_serialized = ProductSerializer(products, many=True).data
    return Response(products_serialized)
