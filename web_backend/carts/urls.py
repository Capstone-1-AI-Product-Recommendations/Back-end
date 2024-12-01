from django.urls import path
from .views import get_cart, add_to_cart, update_cart_item, remove_from_cart, clear_cart

urlpatterns = [
    path('cart/<int:user_id>/', get_cart, name='get_cart'),
    path('cart/add/<int:user_id>/', add_to_cart, name='add_to_cart'),
    path('cart/update/<int:user_id>/', update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:user_id>/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/clear/<int:user_id>/', clear_cart, name='clear_cart'),
]