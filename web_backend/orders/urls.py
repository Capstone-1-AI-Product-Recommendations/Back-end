from django.urls import path
from .views import create_order, update_shipping_address, cancel_order_item, get_user_addresses, add_shipping_address

urlpatterns = [
    path('order/create_order/<int:user_id>/', create_order, name='create_order'),
    path('order/update_shipping/<int:user_id>/', update_shipping_address, name='update_shipping_address'),
    path('order/cancel_order_item/<int:user_id>/<int:order_item_id>/', cancel_order_item, name='cancel_order_item'),
    path('user/<int:user_id>/addresses/', get_user_addresses, name='get_user_addresses'),
    path('user/<int:user_id>/address/add/', add_shipping_address, name='add_shipping_address'),
]
