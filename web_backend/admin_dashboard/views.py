# admin_dashboard/views.py
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.db.models import Q,  Subquery, OuterRef
from datetime import datetime, timedelta
from web_backend.models import *
from django.contrib.auth.hashers import make_password

from django.db.models import Sum
from django.db.models import F
from .serializers import NotificationSerializer, UserBrowsingBehaviorSerializer
from users.serializers import UserSerializer
from products.serializers import CategorySerializer, ProductSerializer
from orders.serializers import OrderSerializer
from seller_dashboard.serializers import AdSerializer
from users.decorators import admin_required
from django.core.validators import validate_email
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
# API để lấy danh sách người dùng (GET)
from django.core.cache import cache
from django.forms import ValidationError 
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from .serializers import CreateUserSerializer
import csv
# API để lấy danh sách người dùng (GET)
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_users(request):
    cache_key = 'users_list'
    cached_users = cache.get(cache_key)
    
    if cached_users:
        return Response(cached_users)
    
    users = User.objects.all()
    serialized_data = UserSerializer(users, many=True).data
    cache.set(cache_key, serialized_data, timeout=86400)  # Cache for 1 day (86400 seconds)
    return Response(serialized_data)

@api_view(['GET'])
@permission_classes([AllowAny])
def export_product(request):
    print("Gia trị url:", request.GET)

    # Kiểm tra quyền admin
    # if not request.user.is_staff:
    #     return Response({'error': 'Permission denied'}, status=403)

    # Lấy danh sách sản phẩm với tối ưu truy vấn
    products = Product.objects.all().select_related('shop').prefetch_related('orderitem_set')

    if not products.exists():
        return Response({'error': 'No products found'}, status=404)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=products.csv'
    response.write(u'\ufeff'.encode('utf8'))  # UTF-8 BOM for Excel compatibility
    writer = csv.writer(response)
    writer.writerow(['Product ID', 'Product Name', 'Quantity', 'Price', 'Shop Name'])

    for product in products:
        total_quantity = sum(item.quantity for item in product.orderitem_set.all())
        total_price = sum(item.price for item in product.orderitem_set.all())
        writer.writerow([
            product.product_id,
            product.name,
            total_quantity,
            total_price,
            product.shop.shop_name,
        ])

    return response

@api_view(['GET'])
@permission_classes([AllowAny])
def export_user(request):
    print("Gia trị url:", request.GET)

    # Lấy danh sách người dùng với tối ưu truy vấn
    users = User.objects.all().select_related('role')

    if not users.exists():
        return Response({'error': 'No users found'}, status=404)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=users.csv'
    response.write(u'\ufeff'.encode('utf8'))  # UTF-8 BOM for Excel compatibility
    writer = csv.writer(response)
    writer.writerow(['User ID', 'Username', 'Email', 'Full Name', 'Role'])

    for user in users:
        writer.writerow([
            user.user_id,
            user.username,
            user.email,
            user.full_name,
            user.role.role_name if user.role else '',
        ])

    return response

@api_view(['GET'])
@permission_classes([AllowAny])
def export_order(request):
    print("Gia trị url:", request.GET)

    # Lấy danh sách đơn hàng với tối ưu truy vấn
    orders = Order.objects.all().select_related('user').prefetch_related('orderitem_set__product__shop', 'payment_set')

    if not orders.exists():
        return Response({'error': 'No orders found'}, status=404)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=orders.csv'
    response.write(u'\ufeff'.encode('utf8'))  # UTF-8 BOM for Excel compatibility
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Product Name', 'Quantity', 'Price', 'Status', 'Transaction', 'Shop Name'])

    for order in orders:
        payment = order.payment_set.first()
        for item in order.orderitem_set.all():
            writer.writerow([
                order.order_id,
                item.product.name,
                item.quantity,
                item.price,
                order.status,
                payment.transaction_id if payment else '',
                item.product.shop.shop_name,
            ])

    return response

# API để thêm người dùng mới (POST)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    data = request.data

    # Check if username already exists in cache
    cache_key = 'users_list'
    users_list = cache.get(cache_key)
    if users_list:
        if any(user['username'] == data.get('username') for user in users_list):
            return Response({"error": "Username already in use."}, status=status.HTTP_400_BAD_REQUEST)
        if any(user['email'] == data.get('email') for user in users_list):
            return Response({"error": "Email already in use."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # If cache is empty, fetch from database and update cache
        users = User.objects.all()
        users_list = UserSerializer(users, many=True).data
        cache.set(cache_key, users_list, timeout=86400)  # Cache for 1 day (86400 seconds)

        if any(user['username'] == data.get('username') for user in users_list):
            return Response({"error": "Username already in use."}, status=status.HTTP_400_BAD_REQUEST)
        if any(user['email'] == data.get('email') for user in users_list):
            return Response({"error": "Email already in use."}, status=status.HTTP_400_BAD_REQUEST)

    # Hash password
    password = data.get('password')
    if password:
        hashed_password = make_password(password)
        data['password'] = hashed_password

    # Set created_at
    data['created_at'] = now()

    # Set role
    role_name = data.get('role_name')
    role_instance, created = Role.objects.get_or_create(role_name=role_name)
    data['role'] = role_instance.pk  # Use pk to get the primary key of the role instance

    # Create user
    serializer = CreateUserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()

        # Update cache
        users_list.append(UserSerializer(user).data)
        cache.set(cache_key, users_list, timeout=86400)  # Cache for 1 day (86400 seconds)

        return Response({"message": "User created successfully. A verification email has been sent."}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_statistics(request):
    # Số lượng người bán (role seller)
    seller_role = Role.objects.get(role_name='seller')
    seller_count = User.objects.filter(role=seller_role).count()

    # Số lượng người dùng (tất cả người)
    user_count = User.objects.count()

    # Số lượng sản phẩm
    product_count = Product.objects.count()

    # Tổng doanh thu của toàn bộ
    total_revenue = Order.objects.aggregate(total_revenue=Sum('total'))['total_revenue'] or 0

    data = {
        'seller_count': seller_count,
        'user_count': user_count,
        'product_count': product_count,
        'total_revenue': total_revenue
    }

    return Response(data, status=status.HTTP_200_OK)

# API để lấy thông tin chi tiết của một người dùng (GET)
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_user_detail(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        serialized_data = UserSerializer(user).data
        return Response(serialized_data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# API để cập nhật thông tin người dùng (PUT)
@api_view(['PUT'])
# @admin_required
@permission_classes([AllowAny])
def update_user(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# API để xóa người dùng (DELETE)
@api_view(['DELETE'])
# @admin_required
@permission_classes([AllowAny])
def delete_user(request, user_id):
    try:
        # Xóa người dùng trong cache
        cache_key = 'users_list'
        users_list = cache.get(cache_key)
        if users_list:
            user_in_cache = next((u for u in users_list if u['user_id'] == user_id), None)
            if user_in_cache:
                users_list = [u for u in users_list if u['user_id'] != user_id]
                cache.set(cache_key, users_list, timeout=86400)  # Cache for 1 day (86400 seconds)

        # Lấy đối tượng người dùng từ cơ sở dữ liệu
        user = User.objects.get(user_id=user_id)

        # Xử lý các bảng liên quan, như shop (nếu có)
        shops = Shop.objects.filter(user_id=user_id)
        for shop in shops:
            # Cập nhật foreign key (user_id) của shop thành None
            shop.user = None
            shop.save()

        # Sau khi xử lý xong, tiến hành xóa người dùng
        user.delete()

        return Response({"message": "User deleted successfully!"}, status=200)

    except IntegrityError as e:
        # Nếu gặp lỗi liên quan đến khóa ngoại, xử lý ngoại lệ
        return Response({"error": str(e)}, status=400)
    except User.DoesNotExist:
        # Nếu người dùng không tồn tại
        return Response({"error": "User not found!"}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_product(request):
    cache_key = 'product_details'
    product_details = cache.get(cache_key)

    if product_details:
        return Response(product_details, status=status.HTTP_200_OK)
    else:
        first_image_subquery = ProductImage.objects.filter(
            product_id=OuterRef('pk')
        ).values('file')[:1]

        products = Product.objects.values(
            'product_id', 'name', 'quantity', 'price', 'created_at',
            shop_name=F('shop__shop_name')
        ).annotate(
            image_file=Subquery(first_image_subquery)
        )
        product_details = list(products)
        cache.set(cache_key, product_details, timeout=86400)  # Cache for 1 day (86400 seconds)
        return Response(product_details, status=status.HTTP_200_OK)

# API để tìm kiếm người dùng dựa trên username, email hoặc role.
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def search_users(request):
    username_query = request.query_params.get('username', '').strip()
    email_query = request.query_params.get('email', '').strip()
    role_query = request.query_params.get('role', '').strip()

    # Kiểm tra nếu không có truy vấn nào
    if not username_query and not email_query and not role_query:
        return Response({'message': 'Please provide at least one search parameter (username, email, or role).'}, status=status.HTTP_400_BAD_REQUEST)

    # Tạo đối tượng Q để xây dựng truy vấn tìm kiếm
    query_conditions = Q()

    # Tìm kiếm theo username nếu có
    if username_query:
        query_conditions &= Q(username__icontains=username_query)

    # Tìm kiếm theo email nếu có
    if email_query:
        query_conditions &= Q(email__icontains=email_query)

    # Tìm kiếm theo role nếu có
    if role_query:
        query_conditions &= Q(role__role_name__icontains=role_query)

    # Truy vấn người dùng với điều kiện tìm kiếm
    users = User.objects.filter(query_conditions).distinct()

    # Kiểm tra và trả về kết quả
    if users.exists():
        serialized_data = UserSerializer(users, many=True).data
        return Response(serialized_data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'No users found matching the query.'}, status=status.HTTP_404_NOT_FOUND)

# API xem danh sách người dùng theo role
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_users_by_role(request, role_name):
    try:
        users = User.objects.filter(role__role_name=role_name)
        serialized_data = UserSerializer(users, many=True).data
        return Response(serialized_data, status=status.HTTP_200_OK)
    except Role.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

# API kiểm tra trạng thái của người dùng (GET)
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def check_user_active_status(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        return Response({
            'user_id': user.user_id,
            'username': user.username,
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# API active/ban tài khoản người dùng (PUT)
@api_view(['PUT'])
# @admin_required
@permission_classes([AllowAny])
def toggle_user_active_status(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        user.is_active = not user.is_active
        user.save()
        return Response({
            'message': f"User {'activated' if user.is_active else 'deactivated'} successfully.",
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# API gửi thông báo cho người dùng (POST)
@api_view(['POST'])
# @admin_required
@permission_classes([AllowAny])
def send_notification(request):
    user_id = request.data.get('user_id')
    message = request.data.get('message')

    if not message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

    if user_id == 'all':
        users = User.objects.all()
    else:
        try:
            users = [User.objects.get(user_id=user_id)]
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    for user in users:
        Notification.objects.create(user=user, message=message, is_read=False)

    return Response({'message': 'Notification(s) sent successfully'}, status=status.HTTP_201_CREATED)

# API xem lịch sử thông báo (GET)
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_notification_history(request, user_id=None):
    if user_id:
        notifications = Notification.objects.filter(user_id=user_id)
    else:
        notifications = Notification.objects.all()

    serialized_data = NotificationSerializer(notifications, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)


# API tạo danh mục sản phẩm mới (POST)
@api_view(['POST'])
# @admin_required
@permission_classes([AllowAny])
def create_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API cập nhật danh mục sản phẩm (PUT)
@api_view(['PUT'])
# @admin_required
@permission_classes([AllowAny])
def update_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategorySerializer(category, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API xóa danh mục sản phẩm (DELETE)
@api_view(['DELETE'])
# @admin_required
@permission_classes([AllowAny])
def delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        category.delete()
        return Response({'message': 'Category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

# API lấy danh sách đơn hàng (GET)
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_orders(request):
    cache_key = 'orders_list'
    cached_orders = cache.get(cache_key)
    
    if cached_orders:
        return Response(cached_orders, status=status.HTTP_200_OK)

    orders = Order.objects.all().order_by('-created_at')  # Sắp xếp theo ngày tạo
    order_data = []

    for order in orders:
        order_items = OrderItem.objects.filter(order=order).select_related('product')
        for item in order_items:
            product = item.product
            shop = product.shop
            product_image = product.images.first().file if product.images.exists() else None
            payment = order.payment_set.first()

            order_data.append({
                'order_id': order.order_id,
                'product_name': product.name,
                'product_image': product_image,
                'quantity': item.quantity,
                'shop_name': shop.shop_name if shop else None,
                'price': item.price,
                'status': order.status,
                'transaction_id': payment.payment_method if payment else None,
            })

    cache.set(cache_key, order_data, timeout=86400)  # Cache for 1 day (86400 seconds)
    return Response(order_data, status=status.HTTP_200_OK)

# API tìm kiếm đơn hàng (GET)
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def search_orders(request):
    query = request.query_params.get('query', '').strip()

    if not query:
        return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Tìm kiếm theo ID đơn hàng, username người dùng, hoặc trạng thái đơn hàng
    orders = Order.objects.filter(
        Q(order_id__icontains=query) |
        Q(user__username__icontains=query) |
        Q(status__icontains=query)
    ).distinct().order_by('-created_at')

    if orders.exists():
        serialized_data = OrderSerializer(orders, many=True).data
        return Response(serialized_data, status=status.HTTP_200_OK)

    return Response({'message': 'No orders found matching the query'}, status=status.HTTP_404_NOT_FOUND)

# API lấy chi tiết đơn hàng (GET)
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_order_detail(request, order_id):
    try:
        # Lấy thông tin đơn hàng
        order = Order.objects.get(order_id=order_id)

        # Truy vấn các sản phẩm trong đơn hàng
        order_items = OrderItem.objects.filter(order=order).select_related('product')

        # Cấu trúc dữ liệu trả về
        serialized_data = {
            'order_id': order.order_id,
            'user_id': order.user.user_id,
            'total': float(order.total),
            'status': order.status,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
            'items': [
                {
                    'order_item_id': item.order_item_id,
                    'product_id': item.product.product_id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.price),
                }
                for item in order_items
            ]
        }

        return Response(serialized_data, status=status.HTTP_200_OK)

    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


# API cập nhật trạng thái đơn hàng (PUT)
@api_view(['PUT'])
# @admin_required
@permission_classes([AllowAny])
def update_order_status(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        order.status = request.data.get('status', order.status)
        order.save()
        return Response({'message': 'Order status updated successfully'}, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# API Xóa đơn hàng
@api_view(['DELETE'])
# @admin_required
@permission_classes([AllowAny])
def delete_order(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        order.delete()
        return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# API Lấy danh sách hành vi duyệt web
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_user_browsing_behaviors(request):
    behaviors = UserBrowsingBehavior.objects.all()
    serialized_data = UserBrowsingBehaviorSerializer(behaviors, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API Lấy chi tiết hành vi duyệt web
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_user_browsing_behavior_detail(request, behavior_id):
    try:
        behavior = UserBrowsingBehavior.objects.get(behavior_id=behavior_id)
        serialized_data = UserBrowsingBehaviorSerializer(behavior).data
        return Response(serialized_data, status=status.HTTP_200_OK)
    except UserBrowsingBehavior.DoesNotExist:
        return Response({'error': 'Browsing behavior not found'}, status=status.HTTP_404_NOT_FOUND)

# API Xóa hành vi duyệt web
@api_view(['DELETE'])
# @admin_required
@permission_classes([AllowAny])
def delete_user_browsing_behavior(request, behavior_id):
    try:
        behavior = UserBrowsingBehavior.objects.get(behavior_id=behavior_id)
        behavior.delete()
        return Response({'message': 'Browsing behavior deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except UserBrowsingBehavior.DoesNotExist:
        return Response({'error': 'Browsing behavior not found'}, status=status.HTTP_404_NOT_FOUND)

# API Hiển thị khách hàng hiện tại
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_current_customers(request):
    customers = User.objects.filter(order__isnull=False).distinct()  # Khách hàng đã có đơn hàng
    serialized_data = UserSerializer(customers, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API Hiển thị khách hàng mới
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_new_customers(request):
    customers = User.objects.filter(order__isnull=True).order_by('-created_at')  # Chưa có đơn hàng, sắp xếp theo thời gian tạo
    serialized_data = UserSerializer(customers, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API Hiển thị khách hàng mục tiêu
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_target_customers(request):
    customers = User.objects.filter(
        Q(userbrowsingbehavior__isnull=False)  # Chỉ lấy thông tin từ userbrowsingbehavior
    ).distinct()
    serialized_data = UserSerializer(customers, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# Hàm tính toán khoảng thời gian
def get_time_range(period):
    now = datetime.now()
    if period == 'day':
        start_time = now - timedelta(days=1)
    elif period == 'week':
        start_time = now - timedelta(weeks=1)
    elif period == 'month':
        start_time = now - timedelta(days=30)
    elif period == 'quarter':  # 3 tháng = 90 ngày
        start_time = now - timedelta(days=90)
    else:
        raise ValueError("Invalid period. Use 'day', 'week', 'month', or 'quarter'.")
    return start_time, now

# API Tổng doanh số, lợi nhuận, doanh thu
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_sales_data(request, period):
    try:
        start_time, end_time = get_time_range(period)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Tổng doanh số
    total_sales = OrderItem.objects.filter(order__created_at__range=(start_time, end_time)).aggregate(
        total_quantity=Sum('quantity')
    )['total_quantity'] or 0

    # Tổng lợi nhuận
    total_profit = OrderItem.objects.filter(order__created_at__range=(start_time, end_time)).aggregate(
        profit=Sum(F('price') - F('cost_price'))  # Giá bán - Giá vốn
    )['profit'] or 0

    # Tổng doanh thu
    total_revenue = Order.objects.filter(created_at__range=(start_time, end_time)).aggregate(
        revenue=Sum('total_price')
    )['revenue'] or 0

    data = {
        "period": period,
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_revenue": total_revenue,
    }
    return Response(data, status=status.HTTP_200_OK)

# API Khách hàng mới
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_new_customers_by_period(request, period):
    """
    API để lấy khách hàng mới trong khoảng thời gian đã chỉ định.
    """
    try:
        start_time, end_time = get_time_range(period)  # Lấy thời gian bắt đầu và kết thúc theo kỳ hạn
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Lọc khách hàng mới dựa trên trường created_at và khoảng thời gian
    new_customers = User.objects.filter(created_at__range=(start_time, end_time)).order_by('-created_at')
    new_customers_count = new_customers.count()

    # Tuỳ chọn: Trả về danh sách chi tiết các khách hàng
    serialized_data = UserSerializer(new_customers, many=True).data

    data = {
        "period": period,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "new_customers_count": new_customers_count,
        "new_customers": serialized_data,  # Bao gồm thông tin chi tiết về khách hàng
    }
    return Response(data, status=status.HTTP_200_OK)

# API lấy thông tin admin
@api_view(['GET'])
# @admin_required
@permission_classes([AllowAny])
def get_admin_info(request):
    try:
        admin_role = Role.objects.get(name='admin')  # Vai trò admin
        admins = User.objects.filter(role=admin_role)

        data = [
            {
                "user_id": admin.user_id,
                "username": admin.username,
                "email": admin.email,
                "full_name": admin.full_name,
                "created_at": admin.created_at,
            }
            for admin in admins
        ]

        return Response({"admins": data}, status=status.HTTP_200_OK)

    except Role.DoesNotExist:
        return Response({"error": "Admin role not found"}, status=status.HTTP_404_NOT_FOUND)

# API chỉnh sửa thông tin admin
@api_view(['PUT'])
# @admin_required
@permission_classes([AllowAny])
def update_admin_info(request, admin_id):
    try:
        admin_role = Role.objects.get(name='admin')
        admin_user = User.objects.get(user_id=admin_id, role=admin_role)
    except Role.DoesNotExist:
        return Response({"error": "Admin role not found"}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"error": "Admin user not found"}, status=status.HTTP_404_NOT_FOUND)

    # Lấy dữ liệu từ request
    data = request.data
    allowed_fields = ['username', 'email', 'full_name']

    # Chỉ cho phép chỉnh sửa các trường đã định sẵn
    for field in allowed_fields:
        if field in data:
            setattr(admin_user, field, data[field])

    # Lưu thông tin
    admin_user.save()

    return Response(
        {
            "message": "Admin information updated successfully",
            "admin": {
                "user_id": admin_user.user_id,
                "username": admin_user.username,
                "email": admin_user.email,
                "full_name": admin_user.full_name,
            }
        },
        status=status.HTTP_200_OK
    )