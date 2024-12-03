from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
# from web_backend.models import Product, Ad
from .serializers import ProductSerializer, CRUDProductSerializer
from seller_dashboard.serializers import AdSerializer
from django.shortcuts import render
# from .models import Product, Category, Comment, User
from web_backend.models import *
from .serializers import ProductSerializer, CommentSerializer, CategorySerializer
from users.serializers import UserSerializer
from django.db.models import Count
import random
from django.db.models import Q
from django.urls import reverse

# Import get_recommended_products correctly
from recommendations.views import get_recommended_products

# API to retrieve product details by product ID
@api_view(['GET'])
def product_detail(request, product_id):
    try:
        product = Product.objects.select_related('category', 'seller') \
                                  .prefetch_related('productrecommendation_set', 'productad_set__ad', 'comment_set') \
                                  .get(product_id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product)
    return Response(serializer.data)

# API to create a new product
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_product(request):
    serializer = CRUDProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API to update a product by product ID
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CRUDProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        updated_product = serializer.save()
        return Response(ProductSerializer(updated_product).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API to delete a product by product ID
@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response({"detail": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

# API to get the featured products (Top 6 products marked as featured)
@api_view(['GET'])
def get_featured_products(request):
    featured_products = Product.objects.filter(is_featured=True)[:6]
    serialized_data = ProductSerializer(featured_products, many=True).data
    return Response(serialized_data)

# API to get trending products (based on user views)
@api_view(['GET'])
def get_trending_products(request):
    trending_products = Product.objects.annotate(
        total_views=Count('userbrowsingbehavior__product')
    ).order_by('-total_views')[:8]
    serialized_data = ProductSerializer(trending_products, many=True).data
    return Response(serialized_data)

# API to get random products (28 random products)
@api_view(['GET'])
def get_random_products(request):
    product_count = Product.objects.count()
    random_ids = random.sample(
        list(Product.objects.values_list('product_id', flat=True)),
        min(28, product_count)
    )
    random_products = Product.objects.filter(product_id__in=random_ids)
    serialized_data = ProductSerializer(random_products, many=True).data
    return Response(serialized_data)

# API to get popular categories (Top 3 categories with most products)
@api_view(['GET'])
def get_popular_categories(request):
    popular_categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('-product_count')[:3]
    serialized_data = CategorySerializer(popular_categories, many=True).data
    return Response(serialized_data)

# API to get all categories
@api_view(['GET'])
def get_all_categories(request):
    all_categories = Category.objects.all()
    serialized_data = CategorySerializer(all_categories, many=True).data
    return Response(serialized_data)

# API to get the latest comments (Top 3 latest comments)
@api_view(['GET'])
def get_latest_comments(request):
    latest_comments = Comment.objects.order_by('-created_at')[:3]
    serialized_data = CommentSerializer(latest_comments, many=True).data
    return Response(serialized_data)

@api_view(['GET'])
def get_ads(request):
    ads = Ad.objects.all()  # Get all ads from the database
    serializer = AdSerializer(ads, many=True)
    return Response(serializer.data)

# API to aggregate data for the homepage
@api_view(['GET'])
def homepage_api(request):
    featured_products = get_featured_products(request).data
    trending_products = get_trending_products(request).data
    random_products = get_random_products(request).data
    recommended_products = get_recommended_products(request).data if request.user.is_authenticated else []
    popular_categories = get_popular_categories(request).data
    latest_comments = get_latest_comments(request).data
    ads = get_ads(request).data  # Assuming you have a function `get_ads()` for fetching ads
    all_categories = get_all_categories(request).data

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

# Bộ lọc theo category
@api_view(['GET'])
def filter_by_category(request):
    category = request.GET.get('category')
    if category:
        products = Product.objects.filter(category__category_name__iexact=category)
        serialized_data = ProductSerializer(products, many=True).data
        return Response(serialized_data, status=200)
    return Response({"message": "Category parameter is required"}, status=400)


# Bộ lọc theo price
@api_view(['GET'])
def filter_by_price(request):
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    try:
        min_price = float(min_price) if min_price else None
        max_price = float(max_price) if max_price else None
    except ValueError:
        return Response({"message": "Price parameters must be numeric"}, status=400)

    if min_price is not None and max_price is not None:
        products = Product.objects.filter(price__gte=min_price, price__lte=max_price)
        serialized_data = ProductSerializer(products, many=True).data
        return Response(serialized_data, status=200)

    return Response({"message": "Both min_price and max_price parameters are required"}, status=400)


# Bộ lọc theo color
@api_view(['GET'])
def filter_by_color(request):
    color = request.GET.get('color')
    if color:
        products = Product.objects.filter(color__iexact=color)
        serialized_data = ProductSerializer(products, many=True).data
        return Response(serialized_data, status=200)
    return Response({"message": "Color parameter is required"}, status=400)


# Bộ lọc theo brand
@api_view(['GET'])
def filter_by_brand(request):
    brand = request.GET.get('brand')
    if brand:
        products = Product.objects.filter(brand__iexact=brand)
        serialized_data = ProductSerializer(products, many=True).data
        return Response(serialized_data, status=200)
    return Response({"message": "Brand parameter is required"}, status=400)


# Bộ lọc theo stock status
@api_view(['GET'])
def filter_by_stock_status(request):
    stock_status = request.GET.get('stock_status')
    if stock_status:
        if stock_status == 'in_stock':
            products = Product.objects.filter(quantity__gt=0)
        elif stock_status == 'out_of_stock':
            products = Product.objects.filter(quantity=0)
        else:
            return Response({"message": "Invalid stock_status value. Use 'in_stock' or 'out_of_stock'."}, status=400)

        serialized_data = ProductSerializer(products, many=True).data
        return Response(serialized_data, status=200)
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

    # Bộ lọc theo category
    category = request.GET.get('category')
    if category:
        products = products.filter(category__category_name__iexact=category)

    # Bộ lọc theo price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            products = products.filter(price__gte=min_price, price__lte=max_price)
        except ValueError:
            return Response({"message": "Price parameters must be numeric"}, status=400)

    # Bộ lọc theo color
    color = request.GET.get('color')
    if color:
        products = products.filter(color__iexact=color)

    # Bộ lọc theo brand
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand__iexact=brand)

    # Bộ lọc theo stock status
    stock_status = request.GET.get('stock_status')
    if stock_status:
        if stock_status == 'in_stock':
            products = products.filter(quantity__gt=0)
        elif stock_status == 'out_of_stock':
            products = products.filter(quantity=0)

    # Bộ lọc theo city và province
    city = request.GET.get('city')
    province = request.GET.get('province')
    if city:
        products = products.filter(seller__user__sellerprofile__city__icontains=city)
    if province:
        products = products.filter(seller__sellerprofile__province__icontains=province)

    # Serialize sản phẩm
    products_serialized = ProductSerializer(products, many=True).data

    # Lọc người bán liên quan đến các sản phẩm đã lọc
    related_sellers_ids = products.values_list('seller_id', flat=True).distinct()
    sellers = SellerProfile.objects.filter(seller_id__in=related_sellers_ids)[:2]
    sellers_serialized = UserSerializer(sellers, many=True).data

    return Response({
        "products": products_serialized,
        "top_sellers": sellers_serialized
    }, status=200)

