from django.urls import path
from .views import delete_shop, update_shop, get_shop_info, get_orders, create_shop, get_order_details, get_comments, get_notifications, get_product_recommendations, ad_performance, sales_report, get_comments_for_product, sales_report_for_product, ad_performance_for_product, get_product_recommendations_for_product, update_order_status
# seller_dashboard/urls.py
from . import views

urlpatterns = [
    # Quản lý đơn hàng    
    path('seller/<int:seller_id>/orders_details/<int:order_id>/', views.get_order_details, name='get_order_details'),

    # Quản lý quảng cáo
#     path('seller/<int:seller_id>/create_ads/<int:product_id>/', views.create_ad, name='create_ad'),
#     path('seller/<int:seller_id>/update_ads/<int:product_id>/<int:ad_id>/', views.update_ad, name='update_ad'),

#     # Quản lý hồ sơ seller
#     path('seller/profile/<int:seller_id>/', views.get_seller_profile, name='get_seller_profile'),
#     path('seller/update_profile/<int:seller_id>/', views.update_seller_profile, name='update_seller_profile'),



    path('seller/orders/<int:seller_id>/', get_orders, name='get_orders'),
    path('seller/<int:seller_id>/orders_details/<int:order_id>/', get_order_details, name='get_order_details'),
    path('seller/<int:seller_id>/update_status/<int:order_item_id>/', update_order_status, name='update_order_status'),
    path('seller/<int:seller_id>/create_shop/', create_shop, name='create_shop'),
    path('seller/shops/info/<int:shop_id>/', get_shop_info, name='get_shop_info'),
    path('seller/<int:seller_id>/shops_update/<int:shop_id>/', update_shop, name='update_shop'),
    path('seller/<int:seller_id>/shops_delete/<int:shop_id>/', delete_shop, name='delete_shop'),

    # Thông báo và phản hồi của người dùng
    path('seller/notifications/<int:seller_id>/', views.get_notifications, name='get_notifications'),
    path('seller/comments/<int:seller_id>/', views.get_comments, name='get_comments'),    

    path('seller/<int:seller_id>/comments_product/<int:product_id>/', get_comments_for_product, name='get_comments_for_product'),


    # Báo cáo và thống kê
    path('seller/sales_report/<int:seller_id>/', views.sales_report, name='sales_report'),
    path('seller/ad_performance/<int:seller_id>/', views.ad_performance, name='ad_performance'),

    # Báo cáo và thống kê theo sản phẩm

    path('seller/<int:seller_id>/sales_report/<int:product_id>/', sales_report_for_product, name='sales_report_for_product'),
    path('seller/<int:seller_id>/ad_performance/<int:product_id>/', ad_performance_for_product, name='ad_performance_for_product'),

    # Quản lý khuyến nghị sản phẩm
    path('seller/product_recommendations/<int:seller_id>/', get_product_recommendations, name='get_product_recommendations'),

    # Khuyến nghị sản phẩm theo sản phẩm cụ thể
    path('seller/<int:seller_id>/product_recommendations/<int:product_id>/', get_product_recommendations_for_product, name='get_product_recommendations_for_product'),

    # Quảng cáo
    path('ads/', views.get_ads, name='get_ads'),  # API lấy danh sách quảng cáo
    path('ads/create/', views.create_ad, name='create_ad'),  # API tạo quảng cáo
    path('ads/homepage-banners/', views.get_homepage_banners, name='get_homepage_banners'),  # API quảng cáo homepage
    
     # Quản lý đơn hàng
    path('seller/orders/<int:seller_id>/', views.get_orders, name='get_orders'),
    path('seller/<int:seller_id>/orders_details/<int:order_id>/', views.get_order_details, name='get_order_details'),

    # Quản lý quảng cáo
#     path('seller/<int:seller_id>/create_ads/<int:product_id>/', views.create_ad, name='create_ad'),
#     path('seller/<int:seller_id>/update_ads/<int:product_id>/<int:ad_id>/', views.update_ad, name='update_ad'),

#     # Quản lý hồ sơ seller
#     path('seller/profile/<int:seller_id>/', views.get_seller_profile, name='get_seller_profile'),
#     path('seller/update_profile/<int:seller_id>/', views.update_seller_profile, name='update_seller_profile'),


    path('seller/orders/<int:seller_id>/', get_orders, name='get_orders'),
    path('seller/<int:seller_id>/orders_details/<int:order_id>/', get_order_details, name='get_order_details'),
    path('seller/<int:seller_id>/update_status/<int:order_item_id>/', update_order_status, name='update_order_status'),
    path('seller/<int:seller_id>/create_shop/', create_shop, name='create_shop'),
    path('seller/shops/info/<int:shop_id>/', get_shop_info, name='get_shop_info'),
    path('seller/<int:seller_id>/shops_update/<int:shop_id>/', update_shop, name='update_shop'),
    path('seller/<int:seller_id>/shops_delete/<int:shop_id>/', delete_shop, name='delete_shop'),

    # Thông báo và phản hồi của người dùng
    path('seller/notifications/<int:seller_id>/', views.get_notifications, name='get_notifications'),
    path('seller/comments/<int:seller_id>/', views.get_comments, name='get_comments'),

    # Thông báo và phản hồi của người dùng theo sản phẩm
    path('seller/<int:seller_id>/comments/<int:product_id>/', views.get_comments_for_product,
         name='get_comments_for_product'),

    path('seller/<int:seller_id>/comments_product/<int:product_id>/', get_comments_for_product, name='get_comments_for_product'),


    # Báo cáo và thống kê
    path('seller/sales_report/<int:seller_id>/', views.sales_report, name='sales_report'),
    path('seller/ad_performance/<int:seller_id>/', views.ad_performance, name='ad_performance'),

    # Báo cáo và thống kê theo sản phẩm
    path('seller/<int:seller_id>/sales_report/<int:product_id>/', views.sales_report_for_product,
         name='sales_report_for_product'),
    path('seller/<int:seller_id>/ad_performance/<int:product_id>/', views.ad_performance_for_product,
         name='ad_performance_for_product'),

    # Quản lý khuyến nghị sản phẩm
    path('seller/product_recommendations/<int:seller_id>/', views.get_product_recommendations,
         name='get_product_recommendations'),

    # Khuyến nghị sản phẩm theo sản phẩm cụ thể
    path('seller/<int:seller_id>/product_recommendations/<int:product_id>/',
         views.get_product_recommendations_for_product, name='get_product_recommendations_for_product'),

    # Quảng cáo
    path('ads/', views.get_ads, name='get_ads'),  # API lấy danh sách quảng cáo
    path('ads/create/', views.create_ad, name='create_ad'),  # API tạo quảng cáo
    path('ads/homepage-banners/', views.get_homepage_banners, name='get_homepage_banners'),  # API quảng cáo homepage
]