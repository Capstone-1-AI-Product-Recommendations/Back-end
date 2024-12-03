from django.urls import path
from .views import product_detail, create_product, update_product, delete_product
from . import views

urlpatterns = [
    path('products/detail/<int:user_id>/<int:product_id>/', product_detail, name='product_detail'),
    path('seller/<int:seller_id>/shops/<int:shop_info_id>/create_product/', create_product, name='create_product'),
    path('seller/<seller_id>/shops/<shop_info_id>/update_product/<product_id>/', update_product, name='update_product'),
    path('seller/<seller_id>/shops/<shop_info_id>/delete_product/<product_id>/', delete_product, name='delete_product'),
    path('featured/', views.get_featured_products, name='featured_products'),
    path('trending/', views.get_trending_products, name='trending_products'),
    path('random/', views.get_random_products, name='random_products'),
    path('popular-categories/', views.get_popular_categories, name='popular_categories'),
    path('all-categories/', views.get_all_categories, name='all_categories'),
    path('latest-comments/', views.get_latest_comments, name='latest_comments'),

    # Filter APIs
    path('filter/category/', views.filter_by_category, name='filter_by_category'),
    path('filter/price/', views.filter_by_price, name='filter_by_price'),
    path('filter/color/', views.filter_by_color, name='filter_by_color'),
    path('filter/brand/', views.filter_by_brand, name='filter_by_brand'),
    path('filter/stock-status/', views.filter_by_stock_status, name='filter_by_stock_status'),

    # Search and filter page API
    path('filter/', views.filter_page, name='filter_page'),
    path('search/', views.filter_page, name='search_products'),
]