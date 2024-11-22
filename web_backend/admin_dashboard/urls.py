# admin_dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_users, name='get-users'), # API lấy tất cả người dùng
    path('users/create/', views.create_user, name='create-user'), # API tạo người dụng mới
    path('users/<int:user_id>/', views.get_user_detail, name='get-user-detail'), # API xem chi tiết người dùng
    path('users/<int:user_id>/update/', views.update_user, name='update-user'), # API cập nhật người dùng
    path('users/<int:user_id>/delete/', views.delete_user, name='delete-user'), # API xóa người dùng
    path('users/search/', views.search_users, name='search_users'),  # API tìm kiếm người dùng
    path('users/role/<str:role_name>/', views.get_users_by_role, name='get_users_by_role'), # API xem danh sách người dùng theo role
    path('users/<int:user_id>/check-active/', views.check_user_active_status, name='check_user_active_status'), # API check trạng thái của người dùng
    path('users/<int:user_id>/toggle-active/', views.toggle_user_active_status, name='toggle_user_active_status'), # API active / ban người dùng

    path('notifications/send/', views.send_notification, name='send_notification'), # API Tạo Thông Báo Cho Người Dùng
    path('notifications/history/', views.get_notification_history, name='get_notification_history'), # API Xem Lịch Sử Thông Báo Được Gửi

    path('categories/', views.create_category, name='create_category'), # API Tạo danh mục sản phẩm
    path('categories/<int:category_id>/', views.update_category, name='update_category'), # API Cập nhật danh mục sản phẩm
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'), # API Xóa 1 danh mục sản phẩm

    path('orders/', views.get_orders, name='get_orders'), # API Lấy danh sách đơn hàng
    path('orders/search/', views.search_orders, name='search_orders'), # API Tìm kiếm đơn hàng
]