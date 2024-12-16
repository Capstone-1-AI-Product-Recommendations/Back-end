from rest_framework.decorators import api_view, parser_classes 
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, F
# from web_backend.models import Product, Ad
from .serializers import ProductSerializer, CRUDProductSerializer
from seller_dashboard.serializers import AdSerializer
from django.shortcuts import render
# from .models import Product, Category, Comment, User
from web_backend.models import *
from .serializers import ProductSerializer, CommentSerializer, CategorySerializer
from web_backend.models import Product, User, Category, Comment, ShopInfo, Shop
from .serializers import DetailProductSerializer, CRUDProductSerializer, ProductSerializer, CommentSerializer, CategorySerializer, DetailCommentSerializer
from django.db.models import Prefetch
from django.shortcuts import render
from users.serializers import UserSerializer
from django.db.models import Count
import random
from django.db.models import Q
from django.urls import reverse
from django.db.models import Sum, Avg, F
from recommendations.views import get_recommended_products
from rest_framework.parsers import MultiPartParser, FormParser


# API to retrieve product details by product ID
@api_view(['GET'])
def product_detail(request, product_id):
    print("user_id", product_id)
    try:
        # Sử dụng select_related cho 'subcategory' và 'shop__user', và prefetch_related cho ảnh và video
        product = Product.objects.select_related('subcategory', 'shop__user') \
                                  .prefetch_related('productrecommendation_set', 'productad_set__ad', 'comment_set', 'images', 'videos') \
                                  .get(product_id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Xử lý description
    description = (
        str(product.description or "")
        .replace("__NEWLINE__", "\n")
        .replace("\\n", "\n")
        .strip()
    )



    
    # Serialize product data
    serializer = DetailProductSerializer(product)
    data = serializer.data
    data['description'] = description
    data['rating'] = product.rating
    data['sales_strategy'] = product.sales_strategy
    data['review_count'] = product.comment_set.count()
    data['detail_product'] = product.detail_product

    return Response(data)

# API to create a new product
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_product(request, seller_id, shop_id):
    try:
        # Kiểm tra seller_id hợp lệ và seller phải có vai trò "Seller"
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can create products."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Kiểm tra shop_id hợp lệ và lấy Shop
    try:
        shop = Shop.objects.get(shop_id=shop_id, user=seller)
    except Shop.DoesNotExist:
        return Response({"detail": "Shop not found or this seller doesn't own this shop."}, status=status.HTTP_404_NOT_FOUND)

    # Thêm seller_id vào request.data
    request.data['seller'] = seller_id
    
    # Khởi tạo serializer với dữ liệu và context seller
    serializer = CRUDProductSerializer(data=request.data, context={'seller': seller})

    if serializer.is_valid():
        # Lưu sản phẩm, điều này sẽ tạo ra các hình ảnh và video liên quan
        # product = serializer.save()
        product = serializer.save(shop=shop)
        # Cập nhật số lượng sản phẩm trong Shop
        shop_info, created = ShopInfo.objects.get_or_create(shop=shop)
        shop_info.product_count += 1
        shop_info.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API to update a product by product ID
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_product(request, seller_id, shop_id, product_id):
    # Kiểm tra seller_id hợp lệ và seller phải có vai trò "Seller"
    try:
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can update products."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Kiểm tra shop_id hợp lệ và lấy Shop
    try:
        shop = Shop.objects.get(shop_id=shop_id, user=seller)
    except Shop.DoesNotExist:
        return Response({"detail": "Shop not found or this seller doesn't own this shop."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy sản phẩm cần cập nhật theo product_id và shop
    try:
        product = Product.objects.get(product_id=product_id, shop=shop)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found in the specified shop."}, status=status.HTTP_404_NOT_FOUND)

    # Cập nhật thông tin sản phẩm
    product_name = request.data.get('name', product.name)
    product_price = request.data.get('price', product.price)
    product_quantity = request.data.get('quantity', product.quantity)
    product_description = request.data.get('description', product.description)

    # Cập nhật các trường của sản phẩm
    product.name = product_name
    product.price = product_price
    product.quantity = product_quantity
    product.description = product_description

    # Xử lý ảnh (nếu có ảnh mới)
    images_data = request.FILES.getlist('images', [])
    if images_data:
        # Xóa các ảnh cũ nếu có
        product.images.all().delete()
        for image_data in images_data:
            image_url = compress_and_upload_image(image_data)  # Hàm xử lý ảnh
            ProductImage.objects.create(product=product, file=image_url)

    # Xử lý video (nếu có video mới)
    videos_data = request.FILES.getlist('videos', [])
    if videos_data:
        # Xóa các video cũ nếu có
        product.videos.all().delete()
        for video_data in videos_data:
            video_url = compress_and_upload_video(video_data)  # Hàm xử lý video
            ProductVideo.objects.create(product=product, file=video_url)

    # Lưu các thay đổi
    product.save()

    return Response({"detail": "Product updated successfully."}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_product(request, seller_id, shop_id, product_id):
    # Kiểm tra seller_id hợp lệ và seller phải có vai trò "Seller"
    try:
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can delete products."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Kiểm tra shop_id hợp lệ và shop thuộc sở hữu của seller
    try:
        shop = Shop.objects.get(shop_id=shop_id, user=seller)
    except Shop.DoesNotExist:
        return Response({"detail": "Shop not found or this seller doesn't own this shop."}, status=status.HTTP_404_NOT_FOUND)

    # Kiểm tra sản phẩm có thuộc về shop hay không
    try:
        product = Product.objects.get(product_id=product_id, shop=shop)
        # Giảm số lượng sản phẩm trong ShopInfo (nếu có liên kết với ShopInfo)
        try:
            shop_info = ShopInfo.objects.get(shop=shop)
            if shop_info.product_count > 0:
                shop_info.product_count -= 1
                shop_info.save()
        except ShopInfo.DoesNotExist:
            pass  # Nếu không có ShopInfo liên kết, bỏ qua
        # Xóa sản phẩm
        product.delete()
        return Response({"detail": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

import re
# API to get the featured products (Top 6 products marked as featured)
@api_view(['GET'])
def get_featured_products(request):
    featured_products = Product.objects.filter(is_featured=True).prefetch_related('productimage_set')[:6]
    serialized_data = [
        {
            "product_id": product.product_id,
            "name": product.name,
            "description": re.sub(
                r'(\n\s*)+', '\n',
                str(product.description or "").replace('__NEWLINE__', '\n').replace('\\n', '\n')
            ).strip(),
            "price": product.price,
            "rating": product.computed_rating,
            "sales_strategy": product.sales_strategy,
            "images": [image.file for image in product.productimage_set.all()]
        }
        for product in featured_products
    ]
    return Response(serialized_data)

# API to get trending products based on various criteria
@api_view(['GET'])
def get_trending_products(request):
    trending_products = Product.objects.annotate(
        total_sales=Sum('orderitem__quantity'),
        total_views=Count('userbrowsingbehavior__product'),
        total_cart_adds=Count('cartitem__product')
    ).annotate(
        trending_score=(
            F('total_sales') * 0.4 +
            F('total_views') * 0.3 +
            F('total_cart_adds') * 0.2 +
            F('rating') * 0.1
        )
    ).order_by('-trending_score').prefetch_related('images')[:12]  # Thay đổi từ 'productimage_set' thành 'images'

    serialized_data = [
        {
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "trending_score": product.trending_score,
            "altImages": [
                image.file for image in product.images.all()  # Sử dụng 'images' thay cho 'productimage_set'
            ]
        }
        for product in trending_products
    ]
    return Response(serialized_data)

# API to get random products (28 random products)
@api_view(['GET'])
def get_random_products(request):
    product_count = Product.objects.count()
    if product_count == 0:
        return Response([])  # Trả về danh sách rỗng nếu không có sản phẩm

    random_ids = random.sample(
        list(Product.objects.values_list('product_id', flat=True)),
        min(28, product_count)
    )
    random_products = Product.objects.filter(product_id__in=random_ids).prefetch_related('images')  # Sửa 'productimage_set' thành 'images'

    serialized_data = [
        {
            "product_id": product.product_id,
            "name": product.name,
            "description": re.sub(
                r'(\n\s*)+', '\n',
                str(product.description or "").replace('__NEWLINE__', '\n').replace('\\n', '\n')
            ).strip(),
            "price": product.price,
            "rating": product.computed_rating,
            "sales_strategy": product.sales_strategy,
            "images": [image.file for image in product.images.all()]  # Sửa 'productimage_set.all()' thành 'images.all()'
        }
        for product in random_products
    ]
    return Response(serialized_data)

# API to get popular categories (Top 3 categories with most subcategories)
@api_view(['GET'])
def get_popular_categories(request):
    # Annotate categories with the count of their subcategories
    popular_categories = Category.objects.annotate(
        subcategory_count=Count('subcategory')  # 'subcategory' là related_name của ForeignKey trong model Subcategory
    ).order_by('-subcategory_count')[:3]  # Get top 3 categories

    # Serialize the data
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
        products = Product.objects.filter(subcategory__category__category_name__iexact=category)
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
    print(f"Initial count: {products.count()}")  # Debug log

    # Tìm kiếm theo từ khóa
    search_term = request.GET.get('search_term', '').strip()
    if search_term:
        products = products.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term)
        )
        print(f"After search: {products.count()}")  # Debug log

    # Bộ lọc theo category
    category = request.GET.get('category', '').strip()
    if category:
        products = products.filter(subcategory__category__category_name__iexact=category)
        print(f"After category: {products.count()}")  # Debug log

    # Bộ lọc theo price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            products = products.filter(price__gte=min_price, price__lte=max_price)
            print(f"After price: {products.count()}")  # Debug log
        except ValueError:
            pass

    # Bộ lọc theo color
    color = request.GET.get('color', '').strip()
    if color:
        products = products.filter(color__iexact=color)
        print(f"After color: {products.count()}")  # Debug log

    # Bộ lọc theo brand
    brand = request.GET.get('brand', '').strip()
    if brand:
        products = products.filter(brand__iexact=brand)
        print(f"After brand: {products.count()}")  # Debug log

    # Bộ lọc theo stock status
    stock_status = request.GET.get('stock_status', '').strip()
    if stock_status:
        if stock_status == 'in_stock':
            products = products.filter(quantity__gt=0)
        elif stock_status == 'out_of_stock':
            products = products.filter(quantity=0)
        print(f"After stock: {products.count()}")  # Debug log

    # Bộ lọc theo city và province
    city = request.GET.get('city', '').strip()
    province = request.GET.get('province', '').strip()
    if city:
        products = products.filter(shop__user__city__icontains=city)
        print(f"After city: {products.count()}")  # Debug log
    if province:
        products = products.filter(shop__user__province__icontains=province)
        print(f"After province: {products.count()}")  # Debug log

    # Serialize sản phẩm
    products_serialized = ProductSerializer(products, many=True).data

    # Lọc shop liên quan
    related_shop_ids = products.values_list('shop_id', flat=True).distinct()
    sellers = User.objects.filter(
        shop__shop_id__in=related_shop_ids,
        role__role_name='Seller'
    )[:2]
    sellers_serialized = UserSerializer(sellers, many=True).data

    return Response({
        "products": products_serialized,
        "top_sellers": sellers_serialized,
        "total_count": len(products_serialized)  # Thêm số lượng sản phẩm vào response
    }, status=200)

@api_view(['GET'])
def search_products(request):
    print("Đã vào được ", request.GET)
    search_term = request.GET.get('search_term', '').strip()
    
    if not search_term:
        return Response(
            {"error": "Please provide a search term"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Tìm kiếm theo category trước
    categories = Category.objects.filter(category_name__icontains=search_term)
    if categories.exists():
        products = Product.objects.filter(subcategory__category__in=categories).prefetch_related('images')
    else:
        # Nếu không tìm thấy category, tìm kiếm theo subcategory
        subcategories = Subcategory.objects.filter(subcategory_name__icontains=search_term)
        if subcategories.exists():
            products = Product.objects.filter(subcategory__in=subcategories).prefetch_related('images')
        else:
            # Nếu không tìm thấy subcategory, tìm kiếm theo tên sản phẩm
            products = Product.objects.filter(name__icontains=search_term).prefetch_related('images')

    # Nếu không tìm thấy kết quả nào, trả về thông báo
    if not products.exists():
        return Response(
            {
                "message": "No products found",
                "products": [],
                "total_count": 0
            }, 
            status=status.HTTP_200_OK
        )

    # Serialize kết quả
    serialized_data = [
        {
            "product_id": product.product_id,
            "name": product.name,
            # "description": product.description
            #     .replace('__NEWLINE__', '\n')  # Xử lý '__NEWLINE__' thành xuống dòng
            #     .replace('\\n', '\n')  # Xử lý chuỗi escape '\\n' thành xuống dòng thực tế
            #     .strip(),  # Loại bỏ khoảng trắng thừa ở đầu hoặc cuối
            "price": product.price,
            "rating": product.rating,  # Thêm rating
            "sales_strategy": product.sales_strategy,  # Thêm sales_strategy
            "images": [
                image.file for image in product.images.all()
            ]
        }
        for product in products
    ]

    return Response({
        "message": "Products found successfully",
        "products": serialized_data,
        "total_count": len(serialized_data)
    }, status=status.HTTP_200_OK)

