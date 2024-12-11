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
from .serializers import OrderCODResponseSerializer, OrderSerializer, OrderItemSerializer
from web_backend.utils import transfer_funds

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
    
@api_view(['GET', 'POST'])
def process_transfer(request, admin_id, order_id, seller_id):
    # Kiểm tra user hiện tại có phải admin hay không
    try:
        admin = User.objects.get(user_id=admin_id)
        if not admin.role or admin.role.role_name != "Admin":
            return Response({"detail": "Only admins can perform this action."}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({"detail": "Admin not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Lấy thông tin đơn hàng
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy seller từ seller_id được truyền vào URL
    try:
        seller = User.objects.get(user_id=seller_id)
        if not seller.role or seller.role.role_name != "Seller":
            return Response({"detail": "Seller not found or invalid role."}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy danh sách các sản phẩm trong đơn hàng thuộc về seller này
    order_items = OrderItem.objects.filter(order=order, product__seller=seller)

    # Tính toán tổng tiền seller nhận được
    total_amount = sum(item.price * item.quantity for item in order_items)

    # Chuyển 0.95 thành Decimal để tránh lỗi kiểu dữ liệu
    net_amount = total_amount * Decimal('0.95')  # Admin giữ lại 5%

    try:
        # Lấy thông tin tài khoản ngân hàng của seller
        bank_account = UserBankAccount.objects.get(user=seller)
    except UserBankAccount.DoesNotExist:
        return Response({"detail": "Bank account not found for seller."}, status=status.HTTP_404_NOT_FOUND)

    # Nếu phương thức là GET: trả về thông tin về transfer
    if request.method == 'GET':
        transfer_details = {
            "seller_name": seller.username,
            "seller_bank_name": bank_account.bank_name,
            "seller_account_number": bank_account.account_number,
            "total_amount": str(total_amount),  # Chuyển Decimal thành str
            "net_amount": str(net_amount),      # Chuyển Decimal thành str
            "order_items": [{"product": item.product.name, "quantity": item.quantity, "price": str(item.price)} for item in order_items]
        }
        return Response(transfer_details)

    # Nếu phương thức là POST: thực hiện chuyển tiền
    elif request.method == 'POST':
        # Thực hiện chuyển tiền qua PayOS
        try:
            response = transfer_funds(
                bank_name=bank_account.bank_name,
                account_number=bank_account.account_number,
                account_holder_name=bank_account.account_holder_name,
                amount=net_amount,
                description=f"Payment for order {order.order_id}"
            )
            if response.status_code == 200:
                return Response({"detail": "Transfer completed successfully."})
            else:
                return Response({"detail": f"Transfer failed: {response.json().get('message', 'Unknown error')}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)