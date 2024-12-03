# admin_dashboard/views.py
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.db.models import Q
from datetime import datetime, timedelta
from web_backend.models import *
# from .models import Notification, UserBrowsingBehavior
# from seller_dashboard.models import Ad
# from users.models import User, Role
# from products.models import Category
# from orders.models import Order, OrderItem
from django.db.models import Sum
from django.db.models import F
from .serializers import NotificationSerializer, UserBrowsingBehaviorSerializer
from users.serializers import UserSerializer
from products.serializers import CategorySerializer
from orders.serializers import OrderSerializer
from seller_dashboard.serializers import AdSerializer
from users.decorators import admin_required

# API để lấy danh sách người dùng (GET)
@api_view(['GET'])
@admin_required
def get_users(request):
    users = User.objects.all()
    serialized_data = UserSerializer(users, many=True).data
    return Response(serialized_data)

# API để thêm người dùng mới (POST)
@api_view(['POST'])
@admin_required
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API để lấy thông tin chi tiết của một người dùng (GET)
@api_view(['GET'])
@admin_required
def get_user_detail(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        serialized_data = UserSerializer(user).data
        return Response(serialized_data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# API để cập nhật thông tin người dùng (PUT)
@api_view(['PUT'])
@admin_required
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
@admin_required
def delete_user(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# API để tìm kiếm người dùng dựa trên username, email hoặc role.
@api_view(['GET'])
@admin_required
def search_users(request):
    query = request.query_params.get('query', '').strip()
    if not query:
        return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)

    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query) |
        Q(role__role_name__icontains=query)
    ).distinct()

    if users.exists():
        serialized_data = UserSerializer(users, many=True).data
        return Response(serialized_data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'No users found matching the query'}, status=status.HTTP_404_NOT_FOUND)

# API xem danh sách người dùng theo role
@api_view(['GET'])
@admin_required
def get_users_by_role(request, role_name):
    try:
        users = User.objects.filter(role__role_name=role_name)
        serialized_data = UserSerializer(users, many=True).data
        return Response(serialized_data, status=status.HTTP_200_OK)
    except Role.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

# API kiểm tra trạng thái của người dùng (GET)
@api_view(['GET'])
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
def get_notification_history(request, user_id=None):
    if user_id:
        notifications = Notification.objects.filter(user_id=user_id)
    else:
        notifications = Notification.objects.all()

    serialized_data = NotificationSerializer(notifications, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)


# API tạo danh mục sản phẩm mới (POST)
@api_view(['POST'])
@admin_required
def create_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API cập nhật danh mục sản phẩm (PUT)
@api_view(['PUT'])
@admin_required
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
@admin_required
def delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        category.delete()
        return Response({'message': 'Category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

# API lấy danh sách đơn hàng (GET)
@api_view(['GET'])
@admin_required
def get_orders(request):
    orders = Order.objects.all().order_by('-created_at')  # Sắp xếp theo ngày tạo
    serialized_data = OrderSerializer(orders, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API tìm kiếm đơn hàng (GET)
@api_view(['GET'])
@admin_required
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
@admin_required
def get_order_detail(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        serialized_data = OrderSerializer(order).data
        return Response(serialized_data, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


# API cập nhật trạng thái đơn hàng (PUT)
@api_view(['PUT'])
@admin_required
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
@admin_required
def delete_order(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        order.delete()
        return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# API Lấy danh sách hành vi duyệt web
@api_view(['GET'])
@admin_required
def get_user_browsing_behaviors(request):
    behaviors = UserBrowsingBehavior.objects.all()
    serialized_data = UserBrowsingBehaviorSerializer(behaviors, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API Lấy chi tiết hành vi duyệt web
@api_view(['GET'])
@admin_required
def get_user_browsing_behavior_detail(request, behavior_id):
    try:
        behavior = UserBrowsingBehavior.objects.get(behavior_id=behavior_id)
        serialized_data = UserBrowsingBehaviorSerializer(behavior).data
        return Response(serialized_data, status=status.HTTP_200_OK)
    except UserBrowsingBehavior.DoesNotExist:
        return Response({'error': 'Browsing behavior not found'}, status=status.HTTP_404_NOT_FOUND)

# API Xóa hành vi duyệt web
@api_view(['DELETE'])
@admin_required
def delete_user_browsing_behavior(request, behavior_id):
    try:
        behavior = UserBrowsingBehavior.objects.get(behavior_id=behavior_id)
        behavior.delete()
        return Response({'message': 'Browsing behavior deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except UserBrowsingBehavior.DoesNotExist:
        return Response({'error': 'Browsing behavior not found'}, status=status.HTTP_404_NOT_FOUND)

# API Hiển thị khách hàng hiện tại
@api_view(['GET'])
@admin_required
def get_current_customers(request):
    customers = User.objects.filter(order__isnull=False).distinct()  # Khách hàng đã có đơn hàng
    serialized_data = UserSerializer(customers, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API Hiển thị khách hàng mới
@api_view(['GET'])
@admin_required
def get_new_customers(request):
    customers = User.objects.filter(order__isnull=True).order_by('-created_at')  # Chưa có đơn hàng, sắp xếp theo thời gian tạo
    serialized_data = UserSerializer(customers, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API Hiển thị khách hàng mục tiêu
@api_view(['GET'])
@admin_required
def get_target_customers(request):
    customers = User.objects.filter(
        Q(userbrowsingbehavior__isnull=False) |  # Có hành vi duyệt web
        Q(adview__isnull=False)  # Xem quảng cáo
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
@admin_required
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
@admin_required
def get_new_customers(request, period):
    try:
        start_time, end_time = get_time_range(period)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Đếm số lượng khách hàng mới
    new_customers_count = User.objects.filter(created_at__range=(start_time, end_time)).count()

    data = {
        "period": period,
        "new_customers": new_customers_count,
    }
    return Response(data, status=status.HTTP_200_OK)

# API lấy thông tin admin
@api_view(['GET'])
@admin_required
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
@admin_required
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