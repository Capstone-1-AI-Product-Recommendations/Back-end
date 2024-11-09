# products/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('featured/', views.get_featured_products, name='featured_products'),
    path('trending/', views.get_trending_products, name='trending_products'),
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
