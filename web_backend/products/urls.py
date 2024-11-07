# products/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('featured/', views.get_featured_products, name='featured_products'),
    path('trending/', views.get_trending_products, name='trending_products'),
    path('popular-categories/', views.get_popular_categories, name='popular_categories'),
    path('all-categories/', views.get_all_categories, name='all_categories'),
    path('latest-comments/', views.get_latest_comments, name='latest_comments'),
]
