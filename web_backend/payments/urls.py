from django.urls import path
from .views import process_payment, payment_cod

urlpatterns = [
    path('process_payment/<int:user_id>/<int:order_id>/', process_payment, name='process_payment'),
    path('payment/cod/<int:user_id>/<int:order_id>/', payment_cod, name='payment_cod')
]