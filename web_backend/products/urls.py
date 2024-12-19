from django.urls import path
from .views import (filter_by_subcategory, product_detail, create_product, update_product, delete_product,
    get_featured_products, get_trending_products, get_random_products,
    get_popular_categories, get_all_categories, get_latest_comments,
    filter_by_category, filter_by_price, filter_by_color, filter_by_brand,
    filter_by_stock_status, filter_page, search_products, get_categories_subcategory, get_top_subcategories, get_product_comments, get_random_relevant_products
)

urlpatterns = [
    # Product display APIs
    path('featured/', get_featured_products, name='featured_products'),
    path('trending/', get_trending_products, name='trending_products'),
    path('random/', get_random_products, name='random_products'),
    path('random-relevant/', get_random_relevant_products, name='random_relevant_products'),
    path('product/<int:product_id>/comments/', get_product_comments, name='get_product_comments'),

    # Categories APIs
    path('popular-categories/', get_popular_categories, name='popular_categories'),   
    path('all-categories/', get_all_categories, name='all_categories'),
    path('sub-categories/', get_categories_subcategory, name='all_categories'),
    path('top-subcategories/', get_top_subcategories, name='get_top_subcategories'),
    
    # Comments API    
    path('latest-comments/', get_latest_comments, name='latest_comments'),
    path('products/detail/<int:product_id>/', product_detail, name='product_detail'),
    path('seller/<int:seller_id>/shops/<int:shop_id>/create_product/', create_product, name='create_product'),
    path('seller/<seller_id>/shops/<shop_id>/update_product/<product_id>/', update_product, name='update_product'),
    path('seller/<seller_id>/shops/<shop_id>/delete_product/<product_id>/', delete_product, name='delete_product'),      
    path('seller/<int:seller_id>/shops/<int:shop_info_id>/create_product/', create_product, name='create_product'),
    path('seller/<seller_id>/shops/<shop_info_id>/update_product/<product_id>/', update_product, name='update_product'),
    path('seller/<seller_id>/shops/<shop_info_id>/delete_product/<product_id>/', delete_product, name='delete_product'),     

    # Filter APIs
    path('filter/category/', filter_by_category, name='filter_by_category'),
    path('filter/subcategory/', filter_by_subcategory, name='filter_by_subcategory'),
    path('filter/price/', filter_by_price, name='filter_by_price'),
    path('filter/color/', filter_by_color, name='filter_by_color'),
    path('filter/brand/', filter_by_brand, name='filter_by_brand'),
    path('filter/stock/', filter_by_stock_status, name='filter_by_stock'),

    # Search API
    path('search/', filter_page, name='search'),
    path('search_products/', search_products, name='search_products'),

    path('filter/stock-status/', filter_by_stock_status, name='filter_by_stock_status'),
    
    #path('filter/', filter_page, name='filter_page'),
]
