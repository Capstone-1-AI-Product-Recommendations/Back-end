from django.urls import path
from .views import product_detail, product_crud


urlpatterns = [
    path('products/detail/<int:pk>/', product_detail, name='product_detail'),
    path('products/crud/', product_crud, name='product_crud'),
    path('products/crud/<int:pk>/', product_crud, name='product_crud'),
]