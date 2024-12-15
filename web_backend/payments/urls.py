from django.urls import path

from .views import *

urlpatterns = [
    # Payment routes
    path('payments/cod/<int:order_id>/', payment_cod, name='cod_payment'),
    path('payos_payment/<int:user_id>/<int:order_id>/', payos, name='payos'),
    path('payment/cod/<int:user_id>/<int:order_id>/', payment_cod, name='payment_cod'),
    path('admin/order/<int:admin_id>/<int:seller_id>/<int:order_id>/', process_transfer, name='process_transfer'),
    path('vnpay_payment/<int:user_id>/<str:order_id>/', vnpay, name='vnpay'),
]