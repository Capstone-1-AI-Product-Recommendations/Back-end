from django.urls import path
from .views import process_payment, payment_cod, process_transfer

urlpatterns = [

    path('process_payment/<int:user_id>/<int:order_id>/', process_payment, name='process_payment'),
    path('payment/cod/<int:user_id>/<int:order_id>/', payment_cod, name='payment_cod'),
    path('admin/order/<int:admin_id>/<int:seller_id>/<int:order_id>/', process_transfer, name='process_transfer'),
]