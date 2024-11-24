from django.urls import path
from .views import get_orders, get_order_details, create_ad, update_ad, get_seller_profile, update_seller_profile, get_comments, get_notifications, get_product_recommendations, ad_performance, sales_report

urlpatterns = [
    # Quản lý đơn hàng
    path('seller/orders/<int:seller_id>/', get_orders, name='get_orders'),
    path('seller/<int:seller_id>/orders_details/<int:order_id>/', get_order_details, name='get_order_details'),

    # Quản lý quảng cáo
    path('seller/<int:seller_id>/create_ads/<int:product_id>/', create_ad, name='create_ad'),
    path('seller/<int:seller_id>/update_ads/<int:product_id>/<int:ad_id>/', update_ad, name='update_ad'),

    # Quản lý hồ sơ seller
    path('seller/profile/<int:seller_id>/', get_seller_profile, name='get_seller_profile'),
    path('seller/update_profile/<int:seller_id>/', update_seller_profile, name='update_seller_profile'),

    # Thông báo và phản hồi của người dùng
    path('seller/notifications/<int:seller_id>/', get_notifications, name='get_notifications'),
    path('seller/comments/<int:seller_id>/', get_comments, name='get_comments'),

    # Báo cáo và thống kê
    path('seller/sales_report/<int:seller_id>/', sales_report, name='sales_report'),
    path('seller/ad_performance/<int:seller_id>/', ad_performance, name='ad_performance'),

    # Quản lý khuyến nghị sản phẩm
    path('seller/product_recommendations/<int:seller_id>/', get_product_recommendations, name='get_product_recommendations'),
]