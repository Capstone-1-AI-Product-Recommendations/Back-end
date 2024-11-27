from django.urls import path
from .views import cod_payment, zalopay_payment, zalopay_callback

urlpatterns = [
    path('payments/cod/<int:order_id>/', cod_payment, name='cod_payment'),
    path('payments/zalopay/<int:order_id>/', zalopay_payment, name='zalopay_payment'),
    path('payments/zalopay_callback/<int:order_id>/', zalopay_callback, name='zalopay_callback'),
]
