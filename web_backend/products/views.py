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
# from recommendations.views import get_recommended_products
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count, F, Sum
from django.db.models.functions import Coalesce
from django.db.models import Value, IntegerField, Case, When
from django.core.cache import cache

CACHE_TIMEOUT = 60 * 15  # Cache timeout in seconds (15 minutes)

@api_view(['GET'])
def get_random_relevant_products(request):
    user_id = request.query_params.get('user_id')  # Lấy user_id từ query parameter
    if not user_id:
        return Response({"error": "Missing user_id"}, status=400)

    cache_key = f'random_relevant_products_{user_id}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    # Lấy các sản phẩm liên quan từ UserBrowsingBehavior
    user_behaviors = UserBrowsingBehavior.objects.filter(user_id=user_id)
    if not user_behaviors.exists():
        return Response([])  # Trả về danh sách rỗng nếu không có hành vi người dùng

    # Lấy danh sách các sản phẩm đã tương tác
    interacted_product_ids = user_behaviors.values_list('product_id', flat=True)

    # Lấy danh sách các danh mục liên quan từ các sản phẩm đã tương tác
    related_categories = Product.objects.filter(
        product_id__in=interacted_product_ids
    ).values_list('subcategory_id', flat=True)

    # Lấy sản phẩm liên quan (trong cùng danh mục hoặc sản phẩm đã tương tác)
    related_products = Product.objects.filter(
        Q(subcategory_id__in=related_categories) | Q(product_id__in=interacted_product_ids)
    ).exclude(product_id__in=interacted_product_ids)  # Loại trừ sản phẩm đã tương tác

    if not related_products.exists():
        return Response([])  # Trả về danh sách rỗng nếu không có sản phẩm liên quan

    # Random lấy tối đa 28 sản phẩm từ các sản phẩm liên quan
    random_products = random.sample(list(related_products), min(28, related_products.count()))

    # Tối ưu hóa việc truy xuất hình ảnh (nếu có model ProductImage)
    random_products = Product.objects.filter(product_id__in=[p.product_id for p in random_products]).prefetch_related('productimage_set')

    # Chuẩn bị dữ liệu JSON trả về
    serialized_data = [
        {
            "product_id": product.product_id,
            "name": product.name,
            "description": re.sub(
                r'(\n\s*)+', '\n',
                str(product.description or "").replace('__NEWLINE__', '\n').replace('\\n', '\n')
            ).strip(),
            "price": product.price,
            "rating": product.rating,
            "sales_strategy": product.sales_strategy,
            "images": [image.file for image in product.productimage_set.all()]
        }
        for product in random_products
    ]

    cache.set(cache_key, serialized_data, CACHE_TIMEOUT)
    return Response(serialized_data)

# API to retrieve product details by product ID
@api_view(['GET'])
def product_detail(request, product_id):
    print("user_id", product_id)

    cache_key = f'product_detail_{product_id}'
    cached_data = cache.get(cache_key)
    if cached_data:
        
        return Response(cached_data)

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

    cache.set(cache_key, data, CACHE_TIMEOUT)
    return Response(data)

@api_view(['GET'])
def get_product_comments(request, product_id):
    try:
        # Get the product
        product = Product.objects.get(product_id=product_id)
        
        # Get comments for the product
        comments = Comment.objects.filter(product=product)
        
        # Serialize comments
        serialized_data = CommentSerializer(comments, many=True).data
        
        return Response(serialized_data, status=status.HTTP_200_OK)
    
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        
        cache.clear()  # Clear cache on product creation
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

    cache.clear()  # Clear cache on product update
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
        cache.clear()  # Clear cache on product deletion
        return Response({"detail": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

import re
# API to get the featured products (Top 6 products marked as featured)
@api_view(['GET'])
def get_featured_products(request):
    cache_key = 'featured_products'
    cached_data = cache.get(cache_key)
    if (cached_data):
        print("cached_data exist")
        return Response(cached_data)

    featured_products = Product.objects.filter(is_featured=True).prefetch_related('images', 'productad_set__ad')[:8]
    serialized_data = [
        {
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "rating": product.computed_rating,
            "sales_strategy": product.sales_strategy,
            "discount_percentage": product.productad_set.first().ad.discount_percentage if product.productad_set.exists() else None,
            "images": [image.file for image in product.images.all()]
        }
        for product in featured_products
    ]
    cache.set(cache_key, serialized_data, CACHE_TIMEOUT)
    return Response(serialized_data)

# API to get trending products based on various criteria
@api_view(['GET'])
def get_trending_products(request):
    cache_key = 'trending_products'
    cached_data = cache.get(cache_key)
    if cached_data:
        print("cached_data exist")
        return Response(cached_data)

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
    ).order_by('-trending_score').prefetch_related('images', 'productad_set__ad')[:12]

    serialized_data = [
        {
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "trending_score": product.trending_score,
            "rating": product.rating,
            "discount_percentage": product.productad_set.first().ad.discount_percentage if product.productad_set.exists() else None,
            "altImages": [
                image.file for image in product.images.all()
            ]
        }
        for product in trending_products
    ]
    print("Đã lưu thông tin sản phẩm")
    cache.set(cache_key, serialized_data, CACHE_TIMEOUT)
    return Response(serialized_data)

# API to get random products (28 random products)
@api_view(['GET'])
def get_random_products(request):
    cache_key = 'random_products'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

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

    cache.set(cache_key, serialized_data, CACHE_TIMEOUT)
    return Response(serialized_data)

# API to get popular categories (Top 3 categories with most subcategories)
@api_view(['GET'])
def get_popular_categories(request):
    cache_key = 'popular_categories'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    # Annotate categories with the count of their subcategories
    popular_categories = Category.objects.annotate(
        subcategory_count=Count('subcategory')  # 'subcategory' là related_name của ForeignKey trong model Subcategory
    ).order_by('-subcategory_count')[:3]  # Get top 3 categories

    # Serialize the data
    serialized_data = CategorySerializer(popular_categories, many=True).data

    cache.set(cache_key, serialized_data, CACHE_TIMEOUT)
    return Response(serialized_data)

# API to get all categories
@api_view(['GET'])
def get_all_categories(request):
    cache_key = 'all_categories'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    all_categories = Category.objects.all()
    serialized_data = CategorySerializer(all_categories, many=True).data

    cache.set(cache_key, serialized_data, CACHE_TIMEOUT)
    return Response(serialized_data)

@api_view(['GET'])
def get_top_subcategories(request):
    cache_key = 'top_subcategories'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    try:
        # Get top 5 subcategories based on product sales
        top_subcategories = Subcategory.objects.annotate(
            total_sales=Coalesce(
                Sum('product__sales_strategy'),
                0
            ),
            product_count=Count('product')
        ).filter(
            product__sales_strategy__gt=0  # Only include subcategories with sales
        ).order_by(
            '-total_sales'
        )[:5]

        # Prepare response data
        serialized_data = [{
            'subcategory_id': subcategory.subcategory_id,
            'subcategory_name': subcategory.subcategory_name,
            'total_sales': subcategory.total_sales,
            'product_count': subcategory.product_count,
            'category_name': subcategory.category.category_name if subcategory.category else None
        } for subcategory in top_subcategories]

        cache.set(cache_key, serialized_data, CACHE_TIMEOUT)
        return Response(serialized_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": f"Error fetching top subcategories: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_categories_subcategory(request):
    cache_key = 'categories_subcategory'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    # Get categories with their subcategories, ordered by total sales_strategy
    top_categories = Category.objects.annotate(
        total_sales=Coalesce(
            Sum('subcategory__product__sales_strategy'),
            0
        )
    ).order_by('-total_sales')[:9]

    serialized_data = []
    for category in top_categories:
        # Get subcategories for each category, ordered by sales
        subcategories = category.subcategory_set.annotate(
            total_sales=Coalesce(
                Sum('product__sales_strategy'),
                0
            )
        ).order_by('-total_sales')

        category_data = {
            'category_id': category.category_id,
            'category_name': category.category_name,
            'total_sales': category.total_sales,
            'subcategories': [{
                'subcategory_id': sub.subcategory_id,
                'subcategory_name': sub.subcategory_name,
                'total_sales': sub.total_sales
            } for sub in subcategories]
        }
        serialized_data.append(category_data)

    cache.set(cache_key, serialized_data, CACHE_TIMEOUT)
    return Response(serialized_data)


# API to get the latest comments (Top 3 latest comments)
@api_view(['GET'])
def get_latest_comments(request):
    cache_key = 'latest_comments'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    latest_comments = Comment.objects.order_by('-created_at')[:3]
    serialized_data = CommentSerializer(latest_comments, many=True).data

    cache.set(cache_key, serialized_data, CACHE_TIMEOUT)
    return Response(serialized_data)

@api_view(['GET'])
def get_ads(request):
    cache_key = 'ads'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    ads = Ad.objects.all()  # Get all ads from the database
    serializer = AdSerializer(ads, many=True)

    cache.set(cache_key, serializer.data, CACHE_TIMEOUT)
    return Response(serializer.data)

# API to aggregate data for the homepage
@api_view(['GET'])
def homepage_api(request):
    cache_key = 'homepage_data'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

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

    cache.set(cache_key, data, CACHE_TIMEOUT)
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

@api_view(['GET'])
def filter_by_subcategory(request):
    try:
        # Get subcategory names from query params
        subcategories = request.GET.getlist('subcategory', [])
        
        if not subcategories:
            return Response({
                "message": "Subcategory parameter is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create query for multiple subcategories
        query = Q()
        for subcategory in subcategories:
            query |= Q(subcategory__subcategory_name__iexact=subcategory)

        # Get products matching any of the subcategories
        products = Product.objects.filter(query).select_related(
            'subcategory', 
            'shop'
        ).prefetch_related('images')

        serialized_data = ProductSerializer(products, many=True).data
        
        return Response({
            "products": serialized_data,
            "total_count": len(serialized_data)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


# Bộ lọc theo tình trạng kho
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

@api_view(['GET'])
def filter_page(request):
    try:
        # Bắt đầu với tất cả sản phẩm
        base_products = Product.objects.all()

        # Tìm kiếm theo từ khóa (search_term)
        search_term = request.GET.get('search_term', '').strip()
        search_results = []  # Sản phẩm từ `search_term`

        if search_term:
            # Tìm kiếm chính xác
            regex_pattern = rf'\b{search_term}\b'
            exact_results = list(base_products.filter(name__iregex=regex_pattern))
            random.shuffle(exact_results)  # Random hóa kết quả chính xác

            # Tìm kiếm gần đúng (loại bỏ các sản phẩm đã có trong kết quả chính xác)
            partial_results = list(
                base_products.filter(name__icontains=search_term)
                .exclude(product_id__in=[p.product_id for p in exact_results])
            )
            random.shuffle(partial_results)  # Random hóa kết quả gần đúng

            # Gộp kết quả chính xác và gần đúng
            search_results = exact_results + partial_results

        # Lọc theo subcategory (nhiều giá trị)
        subcategories = request.GET.getlist('subcategory', [])
        subcategory_results = []
        for subcategory in subcategories:
            subcategory_products = base_products.filter(subcategory__subcategory_name=subcategory)
            subcategory_results.extend(list(subcategory_products))

        random.shuffle(subcategory_results)  # Random hóa kết quả theo subcategory

        # Kết hợp kết quả từ `search_term` và `subcategory`
        combined_results = search_results + [
            product for product in subcategory_results if product not in search_results
        ]

        # Lọc theo price
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price or max_price:
            try:
                if min_price:
                    combined_results = [
                        product for product in combined_results if product.price >= float(min_price)
                    ]
                if max_price:
                    combined_results = [
                        product for product in combined_results if product.price <= float(max_price)
                    ]
            except ValueError:
                return Response({
                    "error": "Invalid price filter values"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Lọc theo rating
        rating = request.GET.get('rating')
        if rating:
            try:
                rating = float(rating)
                combined_results = [
                    product for product in combined_results if product.rating and product.rating >= rating
                ]
            except ValueError:
                return Response({
                    "error": "Invalid rating filter value"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Lọc theo city
        cities = request.GET.getlist('city', [])
        if cities:
            combined_results = [
                product for product in combined_results
                if product.shop and product.shop.user.city in cities
            ]

        # Giới hạn kết quả trả về 100 sản phẩm
        combined_results = combined_results[:100]

        # Serialize kết quả
        products_serialized = [
            {
                "product_id": product.product_id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "quantity": product.quantity,
                "rating": product.rating,
                "stock_status": "in_stock" if product.quantity > 0 else "out_of_stock",
                "subcategory": {
                    "subcategory_id": product.subcategory.subcategory_id if product.subcategory else None,
                    "subcategory_name": product.subcategory.subcategory_name if product.subcategory else None,
                    "category_name": product.subcategory.category.category_name if product.subcategory and product.subcategory.category else None,
                },
                "sales_strategy": product.sales_strategy,
                "images": [image.file for image in product.images.all()]
            }
            for product in combined_results
        ]

        return Response({
            "products": products_serialized,
            "total_count": len(products_serialized)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def search_products(request):
    print("Đã vào được ", request.GET)
    search_term = request.GET.get('search_term', '').strip()
    print("search_term", search_term)
    if not search_term:
        return Response(
            {"error": "Please provide a search term"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Bắt đầu với các sản phẩm tìm kiếm chính xác và gần đúng
    exact_products = Product.objects.none()
    partial_products = Product.objects.none()

    # Tìm kiếm chính xác trên Category
    categories = Category.objects.filter(category_name__iexact=search_term)
    if categories.exists():
        # Nếu tìm thấy Category, lấy Subcategory và tìm Product
        subcategories = Subcategory.objects.filter(category__in=categories)
        if subcategories.exists():
            # Tìm sản phẩm chính xác trong Subcategory
            exact_products = Product.objects.filter(
                subcategory__in=subcategories, name__iexact=search_term
            )
        if not exact_products.exists():
            # Nếu không có sản phẩm chính xác, lấy sản phẩm gần đúng trong Category
            partial_products = Product.objects.filter(
                subcategory__category__in=categories, name__icontains=search_term
            )

    # Nếu không tìm thấy Category
    if not categories.exists() or not exact_products.exists():
        # Tìm kiếm chính xác trên Subcategory
        subcategories = Subcategory.objects.filter(subcategory_name__iexact=search_term)
        if subcategories.exists():
            # Tìm sản phẩm chính xác trong Subcategory
            exact_products = Product.objects.filter(
                subcategory__in=subcategories, name__iexact=search_term
            )
        if not exact_products.exists():
            # Nếu không có sản phẩm chính xác, lấy sản phẩm gần đúng trong Subcategory
            partial_products = Product.objects.filter(
                subcategory__in=subcategories, name__icontains=search_term
            )

    # Nếu không tìm thấy Subcategory
    if not subcategories.exists() or not exact_products.exists():
        # Tìm kiếm chính xác trực tiếp trên Product Name
        exact_products = Product.objects.filter(name__iexact=search_term)
        if not exact_products.exists():
            # Nếu không có sản phẩm chính xác, lấy sản phẩm gần đúng theo Product Name
            partial_products = Product.objects.filter(name__icontains=search_term)

    # Gộp kết quả: chính xác + gần đúng
    combined_products = exact_products | partial_products.exclude(product_id__in=exact_products.values_list('product_id', flat=True))

    # Sắp xếp lại sản phẩm có `name` chứa từ khóa lên đầu
    sorted_results = combined_products.annotate(
    name_contains_keyword=Case(
        When(name__iregex=r'\b' + search_term + r'\b', then=Value(1)),  # Đánh dấu nếu `name` chứa từ khóa dưới dạng từ riêng biệt
        default=Value(0),  # Không đánh dấu nếu không chứa
        output_field=IntegerField()
    )
    ).order_by('-name_contains_keyword', 'name')  # Sắp xếp theo `name_contains_keyword` và `name`

    # Nếu không tìm thấy kết quả nào, trả về thông báo
    if not sorted_results.exists():
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
            "price": product.price,
            "rating": product.rating,
            "sales_strategy": product.sales_strategy,
            "images": [
                image.file for image in product.images.all()
            ],
            "category": product.subcategory.category.category_name if product.subcategory and product.subcategory.category else None,
        }
        for product in sorted_results
    ]

    return Response({
        "message": "Products found successfully",
        "products": serialized_data,
        "total_count": len(serialized_data)
    }, status=status.HTTP_200_OK)
