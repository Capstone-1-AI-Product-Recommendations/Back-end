from django.urls import path
from .views import product_detail, create_product, update_product, delete_product


urlpatterns = [
    path('products/detail/<int:product_id>/', product_detail, name='product_detail'),
    path('products/create_product/', create_product, name='create_product'),
    path('products/update_product/<int:product_id>/', update_product, name='update_product'),
    path('products/delete_product/<int:product_id>/', delete_product, name='delete_product'),
]