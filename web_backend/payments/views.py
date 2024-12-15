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
import hashlib, hmac, json
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .serializers import *
from web_backend.utils import transfer_funds
from datetime import datetime
import urllib.parse 
from django.utils import timezone

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
def payos(request, user_id, order_id):
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
            payment = Payment.objects.create(
                amount=order.total,
                status="Pending",  # Ban đầu trạng thái sẽ là Pending
                payment_method="PayOS",  # Phương thức thanh toán (ví dụ)
                transaction_id=None,  # Ghi sau khi thanh toán hoàn thành
                created_at=timezone.now(),
                updated_at=timezone.now(),
                order=order,
                user=order.user
            )

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
       
class VNPay:
    requestData = {}
    responseData = {}

    def get_payment_url(self, payment_url, secret_key):
        inputData = sorted(self.requestData.items())
        queryString = "&".join(f"{key}={urllib.parse.quote_plus(str(val))}" for key, val in inputData)
        hashValue = self.__hmacsha512(secret_key, queryString)
        return f"{payment_url}?{queryString}&vnp_SecureHash={hashValue}"

    def validate_response(self, secret_key):
        secure_hash = self.responseData.pop('vnp_SecureHash', None)
        self.responseData.pop('vnp_SecureHashType', None)
        sorted_data = sorted(self.responseData.items())
        data_string = "&".join(f"{key}={urllib.parse.quote_plus(str(val))}" for key, val in sorted_data)
        return secure_hash == self.__hmacsha512(secret_key, data_string)

    @staticmethod
    def __hmacsha512(key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


@api_view(['GET', 'POST'])
def vnpay(request, user_id, order_id):
    try:
        order = Order.objects.get(order_id=order_id, user_id=user_id)
        bank_account = UserBankAccount.objects.get(user_id=user_id)

        # Mã ngân hàng (cần kiểm tra và ánh xạ từ account_number -> bank_code nếu có)
        bank_code = "NCB"  # Thay bằng mã ngân hàng thực tế, hoặc để trống nếu không chắc chắn
    except (Order.DoesNotExist, UserBankAccount.DoesNotExist):
        return Response({"error": "Không tìm thấy thông tin đơn hàng hoặc tài khoản ngân hàng"}, status=404)

    if request.method == 'GET':
        return Response({
            "vnp_TxnRef": str(order.order_id),
            "vnp_Amount": int(order.total * 100),
            "vnp_CurrCode": "VND",
            "vnp_OrderInfo": f"Thanh toán đơn hàng {order.order_id}",
            "vnp_OrderType": "other",
            "vnp_Locale": "vn",
            "vnp_BankCode": bank_code,  # Hoặc để ''
        })

    elif request.method == 'POST':
        vnp = VNPay()
        vnp.requestData.update({
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': settings.VNPAY_TMN_CODE,
            'vnp_Amount': int(order.total * 100),
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': str(order.order_id),
            'vnp_OrderInfo': f"Thanh toán đơn hàng {order.order_id}",
            'vnp_OrderType': 'other',
            'vnp_Locale': 'vn',
            'vnp_BankCode': bank_code,  # Hoặc để ''
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
            'vnp_IpAddr': get_client_ip(request),
            'vnp_ReturnUrl': settings.VNPAY_RETURN_URL
        })

        payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
        payment = Payment.objects.create(
            order=order,
            user=order.user,
            amount=order.total,
            status="Pending",
            payment_method="VNPay",
            transaction_id=vnp.requestData['vnp_TxnRef']
        )
        return Response({'payment_url': payment_url})




@api_view(['GET'])
def payment_return(request):
    input_data = request.GET.dict()
    vnp = VNPay()
    vnp.responseData = input_data

    if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
        response_code = input_data.get('vnp_ResponseCode')
        if response_code == '00':
            return Response({"result": "success", "data": input_data})
        return Response({"result": "failure", "data": input_data})

    return Response({"result": "invalid_signature", "data": input_data})


@api_view(['GET'])
def payment_ipn(request):
    input_data = request.GET.dict()
    vnp = VNPay()
    vnp.responseData = input_data

    if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
        response_code = input_data.get('vnp_ResponseCode')
        order_id = input_data.get('vnp_TxnRef')
        amount = int(input_data.get('vnp_Amount', 0)) / 100

        # Logic to verify and update order status goes here

        if response_code == '00':
            return Response({'RspCode': '00', 'Message': 'Confirm Success'})
        return Response({'RspCode': '99', 'Message': 'Payment failed'})
    return Response({'RspCode': '97', 'Message': 'Invalid signature'})