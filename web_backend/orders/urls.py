from django.urls import path
from .views import *

urlpatterns = [
    path('orders/<int:user_id>/', get_orders, name='get_orders'),
    path('orders/<int:user_id>/<int:order_id>/', get_orders, name='get_orders'),
    path('order/create_order/<int:user_id>/', create_order, name='create_order'),
    path('order/update_shipping/<int:user_id>/', update_shipping_address, name='update_shipping_address'),
    path('order/cancel_order_item/<int:user_id>/<int:order_item_id>/', cancel_order_item, name='cancel_order_item'),
]
