from django.shortcuts import render
from .models import Product, Category, Comment, User
from .serializers import ProductSerializer, CommentSerializer, CategorySerializer
from users.serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q
import requests
import random
from django.urls import reverse


# BASE_URL = 'http://localhost:8000'

# API để lấy 6 sản phẩm nổi bật
@api_view(['GET'])
def get_featured_products(request):
    featured_products = Product.objects.filter(is_featured=True)[:6]
    serialized_data = ProductSerializer(featured_products, many=True).data
    return Response(serialized_data)

# API để lấy 8 sản phẩm phổ biến
@api_view(['GET'])
def get_trending_products(request):
    trending_products = Product.objects.annotate(
        total_views=Count('userbrowsingbehavior__product')
    ).order_by('-total_views')[:8]
    serialized_data = ProductSerializer(trending_products, many=True).data
    return Response(serialized_data)

# API để lấy 28 sản phẩm ngẫu nhiên
@api_view(['GET'])
def get_random_products(request):
    product_count = Product.objects.count()
    random_ids = random.sample(
        list(Product.objects.values_list('product_id', flat=True)),
        min(28, product_count)
    )
    random_products = Product.objects.filter(product_id__in=random_ids)
    serialized_data = ProductSerializer(random_products, many=True).data
    print(serialized_data)
    return Response(serialized_data)

# API để lấy danh mục phổ biến
@api_view(['GET'])
def get_popular_categories(request):
    popular_categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('-product_count')[:3]
    serialized_data = CategorySerializer(popular_categories, many=True).data
    return Response(serialized_data)

# API để lấy tất cả danh mục
@api_view(['GET'])
def get_all_categories(request):
    all_categories = Category.objects.all()
    serialized_data = CategorySerializer(all_categories, many=True).data
    return Response(serialized_data)

# API để lấy bình luận mới nhất
@api_view(['GET'])
def get_latest_comments(request):
    latest_comments = Comment.objects.order_by('-created_at')[:3]
    serialized_data = CommentSerializer(latest_comments, many=True).data
    return Response(serialized_data)

# Tổng hợp API cho trang chủ
@api_view(['GET'])
def homepage_api(request):
    # BASE_URL = request.build_absolute_uri('/')[:-1]    
    # featured_products = requests.get(f'{BASE_URL}/products/featured/').json()
    # trending_products = requests.get(f'{BASE_URL}/products/trending/').json()
    # random_products = requests.get(f'{BASE_URL}/products/random/').json()
    # recommended_products = requests.get(f'{BASE_URL}/recommendations/recommended/').json() if request.user.is_authenticated else []
    # popular_categories = requests.get(f'{BASE_URL}/products/popular-categories/').json()
    # latest_comments = requests.get(f'{BASE_URL}/products/latest-comments/').json()
    # ads = requests.get(f'{BASE_URL}/seller_dashboard/ads/').json()
    # all_categories = requests.get(f'{BASE_URL}/products/all-categories/').json()
    
    base_url = request.build_absolute_uri('/')[:-1]  # Lấy url cơ sở chủ động


    featured_products = requests.get(base_url + reverse('featured_products')).json()
    trending_products = requests.get(base_url + reverse('trending_products')).json()
    random_products = requests.get(base_url + reverse('random_products')).json()
    recommended_products = (
        requests.get(base_url + reverse('recommendations:recommended')).json()
        if request.user.is_authenticated else []
    )
    popular_categories = requests.get(base_url + reverse('popular_categories')).json()
    latest_comments = requests.get(base_url + reverse('latest_comments')).json()
    ads = requests.get(base_url + reverse('seller_dashboard:ads')).json()
    all_categories = requests.get(base_url + reverse('all_categories')).json()

    data = {
        'featured_products': featured_products,
        'trending_products': trending_products,
        'random_products': random_products,
        'recommended_products': recommended_products,
        'popular_categories': popular_categories,
        'latest_comments': latest_comments,
        'ads': ads,
        'all_categories': all_categories,
    }
    return Response(data)

# Các API con cho bộ lọc sản phẩm
@api_view(['GET'])
def filter_by_category(request):
    category = request.GET.get('category')
    if category:
        products = Product.objects.filter(category__category_name=category)
        serialized_data = ProductSerializer(products, many=True).data
        return Response(serialized_data)
    return Response({"message": "Category parameter is required"}, status=400)

@api_view(['GET'])
def filter_by_price(request):
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        products = Product.objects.filter(
            Q(price__gte=min_price) & Q(price__lte=max_price)
        )
        serialized_data = ProductSerializer(products, many=True).data
        return Response(serialized_data)
    return Response({"message": "Both min_price and max_price parameters are required"}, status=400)

@api_view(['GET'])
def filter_by_color(request):
    color = request.GET.get('color')
    if color:
        products = Product.objects.filter(color=color)
        serialized_data = ProductSerializer(products, many=True).data
        return Response(serialized_data)
    return Response({"message": "Color parameter is required"}, status=400)

@api_view(['GET'])
def filter_by_brand(request):
    brand = request.GET.get('brand')
    if brand:
        products = Product.objects.filter(brand=brand)
        serialized_data = ProductSerializer(products, many=True).data
        return Response(serialized_data)
    return Response({"message": "Brand parameter is required"}, status=400)

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
        serialized_data = ProductSerializer(products, many=True).data
        return Response(serialized_data)
    return Response({"message": "stock_status parameter is required"}, status=400)

# Tổng hợp API cho Filter_Page với các bộ lọc
@api_view(['GET'])
def filter_page(request):
    products = Product.objects.all()

    # Tìm kiếm theo từ khóa
    search_term = request.GET.get('search_term')
    if search_term:
        products = products.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term)
        )

    # Bộ lọc bổ sung
    category = request.GET.get('category')
    if category:
        products = products.filter(category__category_name=category)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        products = products.filter(
            Q(price__gte=min_price) & Q(price__lte=max_price)
        )

    color = request.GET.get('color')
    if color:
        products = products.filter(color=color)

    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand=brand)

    stock_status = request.GET.get('stock_status')
    if stock_status:
        if stock_status == 'in_stock':
            products = products.filter(stock_status=Product.IN_STOCK)
        elif stock_status == 'on_sale':
            products = products.filter(stock_status=Product.ON_SALE)

    city = request.GET.get('city')
    province = request.GET.get('province')
    if city:
        products = products.filter(address__icontains=city)
    if province:
        products = products.filter(address__icontains=province)

    # Serialize sản phẩm và người bán
    products_serialized = ProductSerializer(products, many=True).data
    related_sellers = {product['seller'] for product in products_serialized if product['seller']}
    sellers = User.objects.filter(id__in=related_sellers)
    # Chỉ lấy top 2 người bán
    top_sellers = sellers[:2]  # Slicing để lấy 2 người bán đầu tiên
    sellers_serialized = UserSerializer(top_sellers, many=True).data

    return Response({
        "products": products_serialized,
        "sellers": sellers_serialized
    })
