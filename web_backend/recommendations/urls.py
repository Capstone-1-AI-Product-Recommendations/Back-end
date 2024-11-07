# recommendations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('recommended/', views.get_recommended_products, name='recommended_products'),
]
