from django.urls import path
from . import views

urlpatterns = [
    path('admin/products/', views.get_product, name='get_product_details'),
    path('admin/statistics/', views.get_statistics, name='get_statistics'),
    path('admin/products/export/', views.export_product, name='export_product'),
    path('admin/users/export/', views.export_user, name='export_user'),
    path('admin/orders/export/', views.export_order, name='export_order'),
    # Users
    path('users/', views.get_users, name='get-users'),  # API lấy tất cả người dùng
    path('users/create/', views.create_user, name='create-user'),  # API tạo người dùng mới
    path('users/<int:user_id>/', views.get_user_detail, name='get-user-detail'),  # API xem chi tiết người dùng
    path('users/<int:user_id>/update/', views.update_user, name='update-user'),  # API cập nhật người dùng
    path('users/<int:user_id>/delete/', views.delete_user, name='delete-user'),  # API xóa người dùng
    path('users/search/', views.search_users, name='search-users'),  # API tìm kiếm người dùng
    path('users/role/<str:role_name>/', views.get_users_by_role, name='get-users-by-role'),  # API xem danh sách người dùng theo role
    path('users/<int:user_id>/check-active/', views.check_user_active_status, name='check-user-active-status'),  # API check trạng thái của người dùng
    path('users/<int:user_id>/toggle-active/', views.toggle_user_active_status, name='toggle-user-active-status'),  # API active / ban người dùng

    # Notifications
    path('notifications/send/', views.send_notification, name='send-notification'),  # API Tạo Thông Báo Cho Người Dùng
    path('notifications/history/', views.get_notification_history, name='get-notification-history'),  # API Xem Lịch Sử Thông Báo Được Gửi

    # Categories
    path('categories/', views.create_category, name='create-category'),  # API Tạo danh mục sản phẩm
    path('categories/<int:category_id>/', views.update_category, name='update-category'),  # API Cập nhật danh mục sản phẩm
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete-category'),  # API Xóa 1 danh mục sản phẩm

    # Orders
    path('orders/', views.get_orders, name='get-orders'),  # API Lấy danh sách đơn hàng
    path('orders/search/', views.search_orders, name='search-orders'),  # API Tìm kiếm đơn hàng
    path('orders/<int:order_id>/', views.get_order_detail, name='get-order-detail'),  # API chi tiết đơn hàng
    path('orders/<int:order_id>/status/', views.update_order_status, name='update-order-status'),  # API Cập nhật trạng thái đơn hàng
    path('orders/<int:order_id>/delete/', views.delete_order, name='delete-order'),  # API Xóa đơn hàng

    # Browsing Behaviors
    path('browsing-behaviors/', views.get_user_browsing_behaviors, name='get-user-browsing-behaviors'),  # API Lấy danh sách hành vi duyệt web
    path('browsing-behaviors/<int:behavior_id>/', views.get_user_browsing_behavior_detail, name='get-user-browsing-behavior-detail'),  # API Lấy chi tiết hành vi duyệt web
    path('browsing-behaviors/<int:behavior_id>/delete/', views.delete_user_browsing_behavior, name='delete-user-browsing-behavior'),  # API Xóa hành vi duyệt web

    # Customers
    path('customers/current/', views.get_current_customers, name='get-current-customers'),  # API Khách hàng hiện tại
    path('customers/new/', views.get_new_customers, name='get-new-customers'),  # API Khách hàng mới
    path('customers/target/', views.get_target_customers, name='get-target-customers'),  # API Khách hàng mục tiêu

    # Stats
    path('stats/sales/<str:period>/', views.get_sales_data, name='get-sales-data'),  # API Tổng doanh số, lợi nhuận, doanh thu
    path('admin_dashboard/stats/new-customers/<str:period>/', views.get_new_customers_by_period, name='new_customers_by_period'),  # API Khách hàng mới (theo thời gian)
    path('stats/new-customers/<str:period>/', views.get_new_customers, name='get-new-customers-stats'),
    # Admin Info
    path('admin/info/', views.get_admin_info, name='get-admin-info'),  # API lấy thông tin admin
    path('admin/info/<int:admin_id>/', views.update_admin_info, name='update-admin-info'),  # API chỉnh sửa thông tin admin
]
