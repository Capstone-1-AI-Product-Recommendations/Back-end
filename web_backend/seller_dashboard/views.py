from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from web_backend.models import Product, Order, OrderItem, Ad, ProductAd, SellerProfile, Notification, Comment, ProductRecommendation
from .serializers import ProductSerializer, AdSerializer, ProductAdSerializer, SellerProfileSerializer, NotificationSerializer, CommentSerializer, ProductRecommendationSerializer
from orders.serializers import OrderSerializer, OrderItemSerializer
from web_backend.models import ShopInfo, Shop, User, Product, Order, OrderItem, Ad, ProductAd, Notification, Comment, ProductRecommendation
from .serializers import ShopInfoSerializer, ShopSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, AdSerializer, ProductAdSerializer, NotificationSerializer, CommentSerializer, ProductRecommendationSerializer
# seller_dashboard/views.py
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from datetime import date
from users.decorators import seller_required
# from .serializers import AdSerializer, ProductSerializer, 
# from .models import Ad, ProductAd
# from products.models import Product


# Quản lý đơn hàng
@api_view(['GET'])
def get_orders(request, seller_id):
    try:
        # Kiểm tra seller_id hợp lệ
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can view orders."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    orders = Order.objects.filter(orderitem__product__seller_id=seller_id).distinct()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_order_details(request, seller_id, order_id):
    try:
        # Kiểm tra seller_id hợp lệ
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can view order details."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    # Lấy thông tin đơn hàng theo order_id và seller_id
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
        # Kiểm tra seller_id hợp lệ
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can update order status."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)    
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

@api_view(['POST'])
def create_shop(request, seller_id):
    # Thêm seller vào validated_data trước khi tạo sản phẩm
    request.data['seller'] = seller_id  # Truyền seller_id vào request data
    # Kiểm tra dữ liệu shop
    serializer = ShopSerializer(data=request.data)

    if serializer.is_valid():
        shop_name = serializer.validated_data.get('shop_name')
        # Tạo shop mới
        shop = Shop.objects.create(shop_name=shop_name, user=seller)
        # Tạo thông tin shop vào ShopInfo
        ShopInfo.objects.create(shop=shop, product_count=0, followers_count=0, is_following=0)
        return Response({
            "message": "Shop created successfully",
            "shop": {
                "shop_id": shop.shop_id,
                "shop_name": shop.shop_name,
                "store_address": seller.address  # Lấy địa chỉ từ User
            }
        }, status=status.HTTP_201_CREATED)    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_shop_info(request, shop_id):
    try:
        # Tìm shop theo shop_id
        shop = Shop.objects.get(shop_id=shop_id)        
        # Lấy thông tin shop từ ShopInfo
        shop_info = ShopInfo.objects.get(shop=shop)        
        # Serialize dữ liệu shop và shop_info
        shop_serializer = ShopSerializer(shop)
        shop_info_serializer = ShopInfoSerializer(shop_info)
        # Trả về thông tin shop và shop info
        return Response({
            "shop": shop_serializer.data,
            "shop_info": shop_info_serializer.data
        }, status=status.HTTP_200_OK)    
    except Shop.DoesNotExist:
        return Response({"detail": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
    except ShopInfo.DoesNotExist:
        return Response({"detail": "Shop information not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['PUT'])
def update_shop(request, seller_id, shop_id):
    # Kiểm tra seller_id có phải là một seller hợp lệ không
    try:
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can update their shop."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    # Kiểm tra shop_id có phải là của seller này không
    try:
        shop = Shop.objects.get(shop_id=shop_id, user=seller)
    except Shop.DoesNotExist:
        return Response({"detail": "Shop not found or not owned by this seller."}, status=status.HTTP_404_NOT_FOUND)
    # Cập nhật thông tin shop
    serializer = ShopSerializer(shop, data=request.data, partial=True)  # partial=True cho phép chỉ cập nhật một số trường
    if serializer.is_valid():
        # Cập nhật hồ sơ người bán
        serializer.save()  # Lưu các thay đổi vào cơ sở dữ liệu
        return Response({
            "message": "Shop updated successfully",
            "shop": serializer.data
        }, status=status.HTTP_200_OK)
    # Trả về lỗi nếu dữ liệu không hợp lệ
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_shop(request, seller_id, shop_id):
    # Kiểm tra seller_id có phải là một seller hợp lệ không
    try:
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can delete their shop."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    # Kiểm tra shop_id có phải là của seller này không
    try:
        shop = Shop.objects.get(shop_id=shop_id, user=seller)
    except Shop.DoesNotExist:
        return Response({"detail": "Shop not found or not owned by this seller."}, status=status.HTTP_404_NOT_FOUND)
    # Xóa các bản ghi liên quan trong shop_info
    try:
        shop_info = ShopInfo.objects.get(shop=shop)
        shop_info.delete()
    except ShopInfo.DoesNotExist:
        pass  # Nếu không tìm thấy, không làm gì cả
    # Xóa shop
    shop.delete()
    return Response({
        "message": "Shop deleted successfully"
    }, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET'])
def get_notifications(request, seller_id):
    try:
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can view notifications."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    # Truy vấn thông báo từ bảng Notification
    notifications = Notification.objects.filter(user__user_id=seller_id)    
    # Chuyển đổi các thông báo thành định dạng JSON
    serializer = NotificationSerializer(notifications, many=True)    
    # Trả về kết quả
    return Response(serializer.data)

@api_view(['GET'])
def get_comments(request, seller_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can view comments."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    comments = Comment.objects.filter(product__seller_id=seller_id)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


# Bình luận cho một sản phẩm
@api_view(['GET'])
def get_comments_for_product(request, seller_id, product_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can view comments for their products."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    comments = Comment.objects.filter(
        product__seller_id=seller_id,
        product_id=product_id
    )
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


# Báo cáo và thống kê
@api_view(['GET'])
def sales_report(request, seller_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can view sales report."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    orders = Order.objects.filter(orderitem__product__seller_id=seller_id).distinct()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def ad_performance(request, seller_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can view ad performance."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    product_ads = ProductAd.objects.filter(product__seller_id=seller_id)
    serializer = ProductAdSerializer(product_ads, many=True)
    return Response(serializer.data)


# Báo cáo doanh thu cho một sản phẩm
@api_view(['GET'])
def sales_report_for_product(request, seller_id, product_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can view sales report for products."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    orders = Order.objects.filter(
        orderitem__product__seller_id=seller_id,
        orderitem__product_id=product_id
    ).distinct()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# Hiệu suất quảng cáo cho một sản phẩm
@api_view(['GET'])
def ad_performance_for_product(request, seller_id, product_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can view ad performance for products."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
    product_ads = ProductAd.objects.filter(
        product__seller_id=seller_id,
        product_id=product_id
    )
    serializer = ProductAdSerializer(product_ads, many=True)
    return Response(serializer.data)


# Quản lý khuyến nghị sản phẩm
@api_view(['GET'])
def get_product_recommendations(request, seller_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Only sellers can view product recommendations."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
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

            # Kết hợp quảng cáo và thông tin sản phẩm liên quan
            serialized_ads.append({
                'ad': AdSerializer(ad).data,
                'related_products': serialized_product_ads
            })

        return Response(serialized_ads, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
