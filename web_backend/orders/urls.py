from django.urls import path
from .views import create_order, update_shipping_address

urlpatterns = [
    path('order/create/<int:user_id>/', create_order, name='create_order'),
    path('order/update_shipping/<int:user_id>/', update_shipping_address, name='update_shipping_address'),
]
