from django.urls import path
from .views import (product_detail, create_product, update_product, delete_product,
    get_featured_products, get_trending_products, get_random_products,
    get_popular_categories, get_all_categories, get_latest_comments,
    filter_by_category, filter_by_price, filter_by_color, filter_by_brand,
    filter_by_stock_status, filter_page
)

urlpatterns = [
    # Product-related URLs
    path('products/detail/<int:product_id>/', product_detail, name='product_detail'),
    path('products/create/', create_product, name='create_product'),
    path('products/update/<int:product_id>/', update_product, name='update_product'),
    path('products/delete/<int:product_id>/', delete_product, name='delete_product'),

    # Product display APIs
    path('featured/', get_featured_products, name='featured_products'),
    path('trending/', get_trending_products, name='trending_products'),
    path('random/', get_random_products, name='random_products'),

    # Categories APIs
    path('popular-categories/', get_popular_categories, name='popular_categories'),
    path('all-categories/', get_all_categories, name='all_categories'),

    # Comments API
    path('latest-comments/', get_latest_comments, name='latest_comments'),
    path('products/detail/<int:user_id>/<int:product_id>/', product_detail, name='product_detail'),
    path('seller/<int:seller_id>/shops/<int:shop_info_id>/create_product/', create_product, name='create_product'),
    path('seller/<seller_id>/shops/<shop_info_id>/update_product/<product_id>/', update_product, name='update_product'),
    path('seller/<seller_id>/shops/<shop_info_id>/delete_product/<product_id>/', delete_product, name='delete_product'),
    path('featured/', get_featured_products, name='featured_products'),
    path('trending/', get_trending_products, name='trending_products'),
    path('random/', get_random_products, name='random_products'),
    path('popular-categories/', get_popular_categories, name='popular_categories'),
    path('all-categories/', get_all_categories, name='all_categories'),
    path('latest-comments/', get_latest_comments, name='latest_comments'),

    # Filter APIs
    path('filter/category/', filter_by_category, name='filter_by_category'),
    path('filter/price/', filter_by_price, name='filter_by_price'),
    path('filter/color/', filter_by_color, name='filter_by_color'),
    path('filter/brand/', filter_by_brand, name='filter_by_brand'),
    path('filter/stock/', filter_by_stock_status, name='filter_by_stock'),

    # Search API
    path('search/', filter_page, name='search_products'),

    # General filter page API (both search and filter)
    path('filter/', filter_page, name='filter_page'),
]
