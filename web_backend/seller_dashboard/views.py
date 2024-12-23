import csv
from itertools import count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from orders.serializers import OrderSerializer, OrderItemSerializer
from web_backend.models import *
from .serializers import ShopInfoSerializer, ShopSerializer, ProductSerializer, SellOrderSerializer, SellOrderItemSerializer, AdSerializer, ProductAdSerializer, NotificationSerializer, CommentSerializer, ProductRecommendationSerializer
# seller_dashboard/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from datetime import date, timedelta
import openpyxl
from users.decorators import seller_required
from django.db.models import F, Case, When, Value, Sum, Count
from django.db.models.functions import Greatest
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, ExtractWeek, ExtractMonth

@api_view(['GET'])
def get_seller_products(request, seller_id):
    try:
        seller = User.objects.get(user_id=seller_id)
        # Kiểm tra seller_id hợp lệ
        if not seller.role or seller.role.role_name != "seller":
            return Response({"detail": "Only sellers can view their products."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy các sản phẩm của shop
    try:
        # seller = User.objects.get(user_id=seller_id)        
        shop = Shop.objects.get(user=seller)
    except Shop.DoesNotExist:
        return Response({"detail": "Shop not found for this seller."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy các sản phẩm của shop
    products = Product.objects.filter(shop=shop).annotate(
        recent_date=Case(
            When(updated_at__gt=F('created_at'), then=F('updated_at')),
            default=F('created_at')
        )
    ).values('product_id', 'name', 'price', 'quantity', 'recent_date')

    # Lấy URL hình ảnh của từng sản phẩm
    product_data = []
    for product in products:
        images = ProductImage.objects.filter(product_id=product['product_id']).values_list('file', flat=True)
        product['images'] = list(images)
        product_data.append(product)

    return Response(product_data, status=status.HTTP_200_OK)


# Quản lý đơn hàng
@api_view(['GET'])
def get_orders(request, seller_id):
    # try:
    #     # Kiểm tra seller_id hợp lệ
    #     seller = User.objects.get(user_id=seller_id)
    #     if not seller.role or seller.role.role_name != "seller":
    #         return Response({"detail": "Only sellers can view orders."}, status=status.HTTP_403_FORBIDDEN)
    # except User.DoesNotExist:
    #     return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)
        
    seller = User.objects.get(user_id=seller_id)

    # Lấy các đơn hàng của seller
    orders = Order.objects.filter(orderitem__product__shop__user=seller).distinct()

    # Chuẩn bị dữ liệu đơn hàng
    order_data = []
    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            product = item.product
            images = ProductImage.objects.filter(product=product).values_list('file', flat=True)
            recent_date = max(order.created_at, order.updated_at)
            payment = Payment.objects.filter(order=order).first()

            order_data.append({
                'full_name': order.user.full_name,
                'product_name': product.name,
                'images': list(images),
                'recent_date': recent_date,
                'payment_method': payment.payment_method if payment else None,
                'price': item.price,
                'status': order.status,
            })
    return Response(order_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_order_details(request, seller_id, order_id):
    try:
        # Kiểm tra seller_id hợp lệ
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "seller":
            return Response({"detail": "Only sellers can view order details."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy thông tin đơn hàng theo order_id và seller_id
    # Sửa lại để truy vấn qua OrderItem và Product
    order = get_object_or_404(Order, order_id=order_id, orderitem__product__shop__user=seller)

    order_items = OrderItem.objects.filter(order=order)
    order_item_serializer = SellOrderItemSerializer(order_items, many=True)
    order_serializer = SellOrderSerializer(order)

    return Response({
        'order': order_serializer.data,
        'items': order_item_serializer.data
    })


@api_view(['GET', 'PUT'])
def update_order_status(request, order_item_id, seller_id):
    try:
        # Kiểm tra seller_id hợp lệ
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "seller":
            return Response({"detail": "Only sellers can update order status."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)    
    
    try:
        # Lấy OrderItem theo order_item_id
        order_item = OrderItem.objects.get(order_item_id=order_item_id)
        # Lấy Order từ OrderItem
        order = order_item.order

        # Kiểm tra xem người bán có phải là chủ của sản phẩm trong OrderItem hay không
        if order_item.product.shop.user.user_id != seller_id:
            return Response({"error": "Bạn không phải là người bán của sản phẩm trong đơn hàng này."}, status=status.HTTP_403_FORBIDDEN)

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
            # Kiểm tra trạng thái hiện tại của đơn hàng
            if order.status == 'Confirmed':
                return Response({"error": "Đơn hàng đã được xác nhận."}, status=status.HTTP_400_BAD_REQUEST)
            elif order.status == 'Canceled':
                return Response({"error": "Đơn hàng đã bị hủy."}, status=status.HTTP_400_BAD_REQUEST)
            # Cập nhật trạng thái đơn hàng từ 'Pending' sang 'Confirmed'
            order.status = 'Confirmed'
            order.save()
            purchased_products = PurchasedProduct.objects.filter(order_id=order.order_id)
            for purchased_product in purchased_products:
                purchased_product.status = 'Confirmed'  # or giá trị trạng thái khác tùy vào yêu cầu
                purchased_product.save()
            return Response({"message": "Trạng thái đơn hàng đã được cập nhật thành công."}, status=status.HTTP_200_OK)
    
    except OrderItem.DoesNotExist:
        return Response({"error": "Sản phẩm trong đơn hàng không tồn tại."}, status=status.HTTP_404_NOT_FOUND)
    except Order.DoesNotExist:
        return Response({"error": "Đơn hàng không tồn tại."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_shop(request, seller_id):
    # Thêm seller vào validated_data trước khi tạo sản phẩm
    mutable_data = request.data.copy()
    mutable_data['seller'] = seller_id  # Thêm seller vào dữ liệu

    # Sử dụng serializer với dữ liệu mới
    serializer = ShopSerializer(data=mutable_data)

    if serializer.is_valid():
        shop_name = serializer.validated_data.get('shop_name')
        try:
            seller = User.objects.get(pk=seller_id)
        except User.DoesNotExist:
            return Response({"error": "Seller not found"}, status=status.HTTP_404_NOT_FOUND)
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
        if not seller.role or seller.role.role_name != "seller":
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
        if not seller.role or seller.role.role_name != "seller":
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
        if not seller.role or seller.role.role_name != "seller":
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
        if not seller.role or seller.role.role_name != "seller":
            return Response({"detail": "Only sellers can view comments."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy các sản phẩm của cửa hàng mà người bán này sở hữu
    products = Product.objects.filter(shop__user=seller)
    
    # Lọc các bình luận của các sản phẩm này
    comments = Comment.objects.filter(product__in=products)
    
    # Serialize dữ liệu
    serializer = CommentSerializer(comments, many=True)
    
    return Response(serializer.data)


# Bình luận cho một sản phẩm
@api_view(['GET'])
def get_comments_for_product(request, seller_id, product_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "seller":
            return Response({"detail": "Only sellers can view comments for their products."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lọc các bình luận cho sản phẩm thuộc cửa hàng của seller
    comments = Comment.objects.filter(
        product__shop__user=seller,  # Lọc sản phẩm của cửa hàng của seller
        product_id=product_id  # Lọc theo product_id
    )
    
    # Serialize dữ liệu
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


# Báo cáo và thống kê
@api_view(['GET'])
def sales_report(request, seller_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "seller":
            return Response({"detail": "Only sellers can view sales report."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lọc các đơn hàng có sản phẩm thuộc cửa hàng của seller
    orders = Order.objects.filter(
        orderitem__product__shop__user=seller  # Lọc sản phẩm của cửa hàng thuộc seller
    ).distinct()

    # Serialize dữ liệu
    serializer = SellOrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def ad_performance(request, seller_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "seller":
            return Response({"detail": "Only sellers can view ad performance."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Truy vấn các quảng cáo cho sản phẩm của seller thông qua Shop
    product_ads = ProductAd.objects.filter(product__shop__user=seller)

    # Serialize dữ liệu
    serializer = ProductAdSerializer(product_ads, many=True)
    return Response(serializer.data)


# Báo cáo doanh thu cho một sản phẩm
@api_view(['GET'])
def sales_report_for_product(request, seller_id, product_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "seller":
            return Response({"detail": "Only sellers can view sales report for products."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Truy vấn shop của seller_id
    try:
        shop = Shop.objects.get(user_id=seller_id)
    except Shop.DoesNotExist:
        return Response({"detail": "Shop for the seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Truy vấn sản phẩm thuộc shop này
    try:
        product = Product.objects.get(product_id=product_id, shop=shop)  # Liên kết với shop
    except Product.DoesNotExist:
        return Response({"detail": "Product not found for this shop."}, status=status.HTTP_404_NOT_FOUND)

    # Lọc đơn hàng liên quan đến sản phẩm của shop này
    orders = Order.objects.filter(
        orderitem__product=product  # Lọc theo sản phẩm
    ).distinct()

    serializer = SellOrderSerializer(orders, many=True)
    return Response(serializer.data)


# Hiệu suất quảng cáo cho một sản phẩm
@api_view(['GET'])
def ad_performance_for_product(request, seller_id, product_id):
    try:
        # Kiểm tra xem seller_id có hợp lệ không
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "seller":
            return Response({"detail": "Only sellers can view ad performance for products."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Truy vấn quảng cáo của sản phẩm trong shop của seller
    product_ads = ProductAd.objects.filter(
        product__shop__user_id=seller_id,  # Liên kết qua shop và user
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
        if not seller.role or seller.role.role_name != "seller":
            return Response({"detail": "Only sellers can view product recommendations."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Sửa lại truy vấn để liên kết qua shop và user
    recommendations = ProductRecommendation.objects.filter(product__shop__user_id=seller_id)
    serializer = ProductRecommendationSerializer(recommendations, many=True)
    return Response(serializer.data)


# Khuyến nghị cho một sản phẩm
@api_view(['GET'])
def get_product_recommendations_for_product(request, seller_id, product_id):
    recommendations = ProductRecommendation.objects.filter(
        product__shop__user_id=seller_id,  # Liên kết qua shop và user
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

@api_view(['GET'])
def export_orders(request, seller_id):
    print("Gia trị url:", request.GET)

    # Kiểm tra quyền
    if request.user.id != int(seller_id):
        return Response({'error': 'Permission denied'}, status=403)

    # Lấy danh sách đơn hàng với tối ưu truy vấn
    orders = Order.objects.filter(orderitem__product__shop__user__user_id=seller_id).distinct() \
        .select_related('user') \
        .prefetch_related('orderitem_set__product', 'payment_set')

    if not orders.exists():
        return Response({'error': 'No orders found for this seller'}, status=404)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=orders.csv'
    response.write(u'\ufeff'.encode('utf8'))  # UTF-8 BOM for Excel compatibility
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Buyer Name', 'Purchase Date', 'Payment Method', 'Product', 'Quantity', 'Price', 'Status'])
    for order in orders:
        payment = order.payment_set.first()
        for item in order.orderitem_set.all():
            writer.writerow([
                order.order_id,
                order.user.full_name,
                order.created_at.strftime('%Y-%m-%d'),
                payment.payment_method if payment else None,
                item.product.name,
                item.quantity,
                item.price,
                order.status,
            ])

    return response

@api_view(['GET'])
def get_sales_summary(request, user_id):
    try:
        # Kiểm tra xem user_id có hợp lệ không
        user = User.objects.get(user_id=user_id)
        if not user.role or user.role.role_name != "seller":
            return Response({"detail": "Only sellers can view sales summary."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy tổng doanh thu và tổng đơn hàng
    orders = Order.objects.filter(orderitem__product__shop__user=user).distinct()
    total_revenue = orders.aggregate(total_revenue=Sum(F('orderitem__price') * F('orderitem__quantity')))['total_revenue'] or 0
    total_orders = orders.count()

    # Tính giá trị đơn trung bình
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0

    return Response({
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_order_value": average_order_value
    }, status=status.HTTP_200_OK)
    

from django.db.models.functions import TruncMonth

@api_view(['GET'])
def get_yearly_sales_summary(request, user_id):
    try:
        # Kiểm tra xem user_id có hợp lệ không
        user = User.objects.get(user_id=user_id)
        if not user.role or user.role.role_name != "seller":
            return Response({"detail": "Only sellers can view sales summary."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy tổng doanh thu và tổng đơn hàng theo tháng
    orders = Order.objects.filter(orderitem__product__shop__user=user).annotate(month=TruncMonth('created_at')).values('month').annotate(
        total_revenue=Sum(F('orderitem__price') * F('orderitem__quantity')),
        total_orders=Count('order_id')
    ).order_by('month')

    # Chuẩn bị dữ liệu trả về
    monthly_sales = []
    for order in orders:
        month_name = f"T{order['month'].month}"
        monthly_sales.append({
            'name': month_name,
            'sales': order['total_revenue'] or 0,
            'orders': order['total_orders']
        })

    return Response({'year': monthly_sales}, status=status.HTTP_200_OK)

from django.db.models import Count

@api_view(['GET'])
def get_shop_categories(request, shop_id):
    try:
        # Kiểm tra xem shop_id có hợp lệ không
        shop = Shop.objects.get(shop_id=shop_id)
    except Shop.DoesNotExist:
        return Response({"detail": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy số lượng sản phẩm theo danh mục
    categories = Category.objects.filter(subcategory__product__shop=shop).annotate(
        product_count=Count('subcategory__product')
    ).values('category_name', 'product_count')

    # Chuẩn bị dữ liệu trả về
    category_data = []
    for category in categories:
        category_data.append({
            'name': category['category_name'],
            'value': category['product_count']
        })

    return Response(category_data, status=status.HTTP_200_OK)