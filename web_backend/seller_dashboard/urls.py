from django.urls import path
from .views import order_list, update_order_status, create_coupon, review_list

urlpatterns = [
    path('seller/orders', order_list, name='order_list'),
    path('seller/orders/<int:order_id>/status', update_order_status, name='update_order_status'),
    path('seller/coupons', create_coupon, name='create_coupon'),
    path('seller/reviews', review_list, name='review_list'),
]
