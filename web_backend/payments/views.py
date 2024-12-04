from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from web_backend.models import Order, OrderItem, User, Payment, ShippingAddress, UserBankAccount
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from urllib.parse import quote
from payos import PayOS
from payos.type import PaymentData, ItemData
import hashlib
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .serializers import OrderCODResponseSerializer

# Khởi tạo đối tượng PayOS
payOS = PayOS(
    client_id=settings.PAYOS_CLIENT_ID,
    api_key=settings.PAYOS_API_KEY,
    checksum_key=settings.PAYOS_CHECKSUM_KEY
)

def calculate_checksum(data, checksum_key):
    sorted_data = sorted(data.items())
    query_string = '&'.join(f"{key}={value}" for key, value in sorted_data)
    query_string += f"&key={checksum_key}"
    return hashlib.sha256(query_string.encode('utf-8')).hexdigest()

@api_view(['GET', 'POST'])
def process_payment(request, user_id, order_id):
    # Lọc đơn hàng với user_id và order_id
    order = Order.objects.filter(
        order_id=order_id,
        user_id=user_id
    ).exclude(
        status="Canceled"
    ).filter(
        status__in=["Pending", "Processing"]
    ).first()

    if order is None:
        return Response({"error": "Order not found or not in valid status."}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        # Trả về thông tin thanh toán nếu yêu cầu là GET
        order_items = OrderItem.objects.filter(order=order)
        items = []
        for item in order_items:
            items.append({
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": str(item.price)
            })
        return Response({
            "order_id": order.order_id,
            "total": str(order.total),
            "status": order.status,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": items
        }, status=status.HTTP_200_OK)
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        user_id = request.POST.get('user_id')
        # Dữ liệu thanh toán
        items = []
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            items.append(ItemData(name=item.product.name, quantity=item.quantity, price=int(item.price)))  # Sử dụng ItemData
        description = f"Thanh toán cho đơn hàng {order.order_id}"
        description = description[:25]
        # Tạo đối tượng PaymentData hợp lệ
        payment_data = PaymentData(
            orderCode=int(order.order_id),  # Đảm bảo orderCode là kiểu int
            amount=int(order.total),  # Số tiền thanh toán
            description=description,
            items=items,  # Các mặt hàng trong đơn
            cancelUrl="http://localhost:8000/cancel",  # URL khi thanh toán bị hủy
            returnUrl="http://localhost:8000/return"  # URL khi thanh toán thành công
        )
        # Khởi tạo đối tượng PayOS
        try:
            payos = PayOS(
                client_id=settings.PAYOS_CLIENT_ID,
                api_key=settings.PAYOS_API_KEY,
                checksum_key=settings.PAYOS_CHECKSUM_KEY
            )
            # Tạo liên kết thanh toán
            payment_link = payos.createPaymentLink(paymentData=payment_data)
            
            # Trả về URL thanh toán cho người dùng
            return Response({
                'payment_url': payment_link.checkoutUrl  # Lấy URL thanh toán
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Payment processing failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET', 'POST'])
def payment_cod(request, user_id, order_id):
    # Kiểm tra xem user_id và order_id có hợp lệ không
    user = get_object_or_404(User, user_id=user_id)
    order = get_object_or_404(Order, order_id=order_id, user=user)

    # Lấy thông tin Shipping Address của người nhận
    shipping_address = get_object_or_404(ShippingAddress, user=user)

    # Lấy thông tin các món hàng trong order
    order_items = OrderItem.objects.filter(order=order)
    total_amount = Decimal(0)

    # Tạo danh sách các món hàng
    items_details = []
    for item in order_items:
        total_amount += item.price * item.quantity
        items_details.append({
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": str(item.price),
            "total_price": str(item.price * item.quantity)
        })

    # Nếu yêu cầu là GET, trả về thông tin đơn hàng
    if request.method == 'GET':
        response_data = {
            "total_amount": str(total_amount),
            "user_name": user.full_name,
            "shipping_address": {
                "recipient_name": shipping_address.recipient_name,
                "recipient_phone": shipping_address.recipient_phone,
                "recipient_address": shipping_address.recipient_address
            },
            "items": items_details
        }
        return Response(response_data, status=status.HTTP_200_OK)

    # Nếu yêu cầu là POST, xử lý thanh toán COD
    elif request.method == 'POST':
        # Tạo Payment cho đơn hàng, thanh toán COD
        payment = Payment.objects.create(
            order=order,
            user=user,
            amount=total_amount,
            status="Pending",
            payment_method="COD",  # Phương thức thanh toán là COD
            transaction_id="COD-" + str(order.order_id)  # Mã giao dịch giả cho COD
        )

        # Dữ liệu trả về
        response_data = {
            "message": "Đơn hàng đang được xử lý",
            "payment_status": payment.status,
            "payment_method": payment.payment_method,
            "total_amount": str(total_amount),
            "user_name": user.full_name,
            "shipping_address": {
                "recipient_name": shipping_address.recipient_name,
                "recipient_phone": shipping_address.recipient_phone,
                "recipient_address": shipping_address.recipient_address
            },
            "items": items_details
        }

        # Serialize dữ liệu và trả về response
        return Response(response_data, status=status.HTTP_201_CREATED)