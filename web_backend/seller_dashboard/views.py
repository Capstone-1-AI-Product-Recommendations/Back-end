from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from web_backend.models import Product, Order, OrderItem, Ad, ProductAd, SellerProfile, Notification, Comment, ProductRecommendation
from .serializers import ProductSerializer, OrderSerializer, OrderItemSerializer, AdSerializer, ProductAdSerializer, SellerProfileSerializer, NotificationSerializer, CommentSerializer, ProductRecommendationSerializer
# seller_dashboard/views.py
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from datetime import date
from users.decorators import seller_required
# from .serializers import AdSerializer, ProductSerializer, ProductAdSerializer
# from .models import Ad, ProductAd
# from products.models import Product

# Quản lý đơn hàng
@api_view(['GET'])
def get_orders(request, seller_id):
    orders = Order.objects.filter(orderitem__product__seller_id=seller_id).distinct()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_order_details(request, seller_id, order_id):
    order = get_object_or_404(Order, order_id=order_id, orderitem__product__seller_id=seller_id)
    order_items = OrderItem.objects.filter(order=order)
    order_item_serializer = OrderItemSerializer(order_items, many=True)
    order_serializer = OrderSerializer(order)
    return Response({
        'order': order_serializer.data,
        'items': order_item_serializer.data
    })

@api_view(['GET', 'PUT'])
def update_order_status(request, order_item_id, seller_id):
    try:
        # Lấy OrderItem theo order_item_id
        order_item = OrderItem.objects.get(order_item_id=order_item_id)

        # Lấy Order từ OrderItem
        order = order_item.order

        if request.method == 'GET':
            # Trả về thông tin đơn hàng và trạng thái
            return Response({
                "order_id": order.order_id,
                "status": order.status,
                "total_amount": order.total,
                "user_id": order.user.user_id,
                "product_name": order_item.product.name,
                "quantity": order_item.quantity,
                "product_price": order_item.price,
            }, status=status.HTTP_200_OK)

        elif request.method == 'PUT':
            # Kiểm tra xem seller_id có phải là người bán của sản phẩm trong OrderItem không
            if order_item.product.seller.user_id != seller_id:
                return Response({"error": "Bạn không phải là người bán của sản phẩm trong đơn hàng này."}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra trạng thái hiện tại của đơn hàng
            if order.status == 'Confirmed':
                return Response({"error": "Đơn hàng đã được xác nhận."}, status=status.HTTP_400_BAD_REQUEST)
            elif order.status == 'Canceled':
                return Response({"error": "Đơn hàng đã bị hủy."}, status=status.HTTP_400_BAD_REQUEST)

            # Cập nhật trạng thái đơn hàng từ 'Pending' sang 'Confirmed'
            order.status = 'Confirmed'
            order.save()

            return Response({"message": "Trạng thái đơn hàng đã được cập nhật thành công."}, status=status.HTTP_200_OK)

    except OrderItem.DoesNotExist:
        return Response({"error": "Sản phẩm trong đơn hàng không tồn tại."}, status=status.HTTP_404_NOT_FOUND)
    except Order.DoesNotExist:
        return Response({"error": "Đơn hàng không tồn tại."}, status=status.HTTP_404_NOT_FOUND)
    
# Quản lý quảng cáo (Ad)
@api_view(['POST'])
def create_ad(request, seller_id, product_id):
    try:
        # Kiểm tra sản phẩm có tồn tại và thuộc về seller hay không
        product = Product.objects.get(product_id=product_id, seller_id=seller_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product does not belong to this seller or does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    # Tạo mới quảng cáo
    ad_data = request.data.copy()
    ad_serializer = AdSerializer(data=ad_data)
    if ad_serializer.is_valid():
        ad = ad_serializer.save()  # Lưu quảng cáo
        # Tạo liên kết giữa quảng cáo và sản phẩm
        product_ad = {
            "product": product.product_id,
            "ad": ad.ad_id
        }
        product_ad_serializer = ProductAdSerializer(data=product_ad)
        if product_ad_serializer.is_valid():
            product_ad_serializer.save()
            return Response({
                "ad": ad_serializer.data,
                "product_ad": product_ad_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            # Xóa quảng cáo nếu liên kết thất bại
            ad.delete()
            return Response(product_ad_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(ad_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_ad(request, seller_id, ad_id, product_id):
    try:
        # Kiểm tra xem sản phẩm thuộc seller có tồn tại không
        product = Product.objects.get(product_id=product_id, seller_id=seller_id)        
        # Kiểm tra xem quảng cáo liên kết với sản phẩm này có tồn tại không
        product_ad = ProductAd.objects.get(product=product, ad_id=ad_id)
        ad = product_ad.ad  # Truy xuất quảng cáo từ ProductAd        
    except (Product.DoesNotExist, ProductAd.DoesNotExist):
        return Response(
            {"error": "Ad or product does not exist for this seller."},
            status=status.HTTP_404_NOT_FOUND
        )
    # Tiến hành cập nhật quảng cáo
    serializer = AdSerializer(ad, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Quản lý hồ sơ seller
@api_view(['GET'])
def get_seller_profile(request, seller_id):
    seller_profile = get_object_or_404(SellerProfile, user_id=seller_id)
    serializer = SellerProfileSerializer(seller_profile)
    return Response(serializer.data)

@api_view(['PUT'])
def update_seller_profile(request, seller_id):
    # Lấy hồ sơ người bán dựa trên seller_id
    seller_profile = get_object_or_404(SellerProfile, user_id=seller_id)
    # Chỉ cần cập nhật các trường khác như store_name, store_address
    serializer = SellerProfileSerializer(seller_profile, data=request.data, partial=True)  # partial=True để chỉ cập nhật các trường cần thiết
    if serializer.is_valid():
        # Cập nhật hồ sơ người bán
        serializer.save()
        return Response(serializer.data)    
    # Trả về lỗi nếu dữ liệu không hợp lệ
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Thông báo và Quản lý Phản hồi 
@api_view(['GET'])
def get_notifications(request, seller_id):
    notifications = Notification.objects.filter(user__seller_profile__user_id=seller_id)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_comments(request, seller_id):
    comments = Comment.objects.filter(product__seller_id=seller_id)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

# Bình luận cho một sản phẩm
@api_view(['GET'])
def get_comments_for_product(request, seller_id, product_id):
    comments = Comment.objects.filter(
        product__seller_id=seller_id,
        product_id=product_id
    )
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

# Báo cáo và thống kê
@api_view(['GET'])
def sales_report(request, seller_id):
    orders = Order.objects.filter(orderitem__product__seller_id=seller_id).distinct()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def ad_performance(request, seller_id):
    product_ads = ProductAd.objects.filter(product__seller_id=seller_id)
    serializer = ProductAdSerializer(product_ads, many=True)
    return Response(serializer.data)

# Báo cáo doanh thu cho một sản phẩm
@api_view(['GET'])
def sales_report_for_product(request, seller_id, product_id):
    orders = Order.objects.filter(
        orderitem__product__seller_id=seller_id,
        orderitem__product_id=product_id
    ).distinct()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

# Hiệu suất quảng cáo cho một sản phẩm
@api_view(['GET'])
def ad_performance_for_product(request, seller_id, product_id):
    product_ads = ProductAd.objects.filter(
        product__seller_id=seller_id,
        product_id=product_id
    )
    serializer = ProductAdSerializer(product_ads, many=True)
    return Response(serializer.data)

# Quản lý khuyến nghị sản phẩm
@api_view(['GET'])
def get_product_recommendations(request, seller_id):
    recommendations = ProductRecommendation.objects.filter(product__seller_id=seller_id)
    serializer = ProductRecommendationSerializer(recommendations, many=True)
    return Response(serializer.data)

# Khuyến nghị cho một sản phẩm
@api_view(['GET'])
def get_product_recommendations_for_product(request, seller_id, product_id):
    recommendations = ProductRecommendation.objects.filter(
        product__seller_id=seller_id,
        product_id=product_id
    )
    serializer = ProductRecommendationSerializer(recommendations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@seller_required
def get_ads(request):
    ads = Ad.objects.all()
    serialized_data = AdSerializer(ads, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API tạo quảng cáo
@api_view(['POST'])
@seller_required
def create_ad(request):
    serializer = AdSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Ad created successfully',
            'ad': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API để lấy danh sách tối đa 3 quảng cáo dành cho banner trang homepage. (Chỉ trả về những quảng cáo đang trong thời gian hiệu lực.)
@api_view(['GET'])
def get_homepage_banners(request):
    """
    Mỗi quảng cáo bao gồm thông tin sản phẩm liên quan nếu có.
    """
    try:
        today = date.today()
        # Lọc các quảng cáo đang hoạt động và lấy tối đa 3 quảng cáo mới nhất
        active_ads = Ad.objects.filter(start_date__lte=today, end_date__gte=today).order_by('-start_date')[:3]

        # Serialize dữ liệu quảng cáo
        serialized_ads = []
        for ad in active_ads:
            # Tìm product ads liên quan đến quảng cáo hiện tại
            product_ads = ProductAd.objects.filter(ad=ad)
            serialized_product_ads = ProductAdSerializer(product_ads, many=True).data

            # Kết hợp thông tin quảng cáo và sản phẩm liên quan
            ad_data = AdSerializer(ad).data
            ad_data['related_products'] = serialized_product_ads  # Thêm sản phẩm liên quan
            serialized_ads.append(ad_data)

        return Response(serialized_ads, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

