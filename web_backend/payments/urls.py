from django.urls import path
from .views import cod_payment, zalopay_payment, payment_callback

urlpatterns = [
    # Payment routes
    path('payments/cod/<int:order_id>/', cod_payment, name='cod_payment'),
    path('payments/zalopay/<int:order_id>/', zalopay_payment, name='zalopay_payment'),

    # Callback from ZaloPay (order_id may not be necessary for callback)
    path('payments/zalopay_callback/', payment_callback, name='payment_callback'),
]
