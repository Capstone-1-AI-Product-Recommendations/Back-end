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
import hashlib, hmac
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .serializers import OrderCODResponseSerializer, OrderSerializer, OrderItemSerializer
from web_backend.utils import transfer_funds
from django.utils import timezone
from datetime import datetime
from urllib.parse import urlencode

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
       
# Hàm chuyển đổi dữ liệu cho VNPay
def convert_data_for_vnpay(order):
    """
    Hàm chuyển đổi dữ liệu từ DB phù hợp với yêu cầu của VNPay.
    """
    # Chuyển đổi order_id (số nguyên)
    order_id = int(order.order_id)
    
    # Chuyển đổi total_amount (tính theo đồng, nhân với 100)
    total_amount = int(order.total * 100)
    
    # Chuyển đổi created_at sang định dạng yyyyMMddHHmmss
    created_at = order.created_at.strftime('%Y%m%d%H%M%S')
    
    # Lấy thông tin người dùng
    user = order.user
    
    # Lấy địa chỉ IP từ request nếu có
    ip_addr = "127.0.0.1"  # Bạn có thể lấy địa chỉ IP từ request

    # Chuyển đổi các tham số thành dictionary
    data = {
        'order_id': order_id,
        'total_amount': total_amount,
        'created_at': created_at,
        'user_id': user.user_id,
        'email': user.email,
        'ip_addr': ip_addr,
    }
    
    return data

# Lớp VNPay dùng để tạo URL thanh toán
class VNPay:
    def __init__(self, config):
        self.config = config

    def create_payment_url(self, order_data):
        # Lấy thông tin cấu hình
        vnp_TmnCode = self.config['vnp_TmnCode']
        vnp_HashSecret = self.config['vnp_HashSecret']
        vnp_Url = self.config['vnp_Url']
        vnp_ReturnUrl = self.config['vnp_ReturnUrl']

        # Tạo tham số thanh toán từ dữ liệu đã chuyển đổi
        params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": vnp_TmnCode,
            "vnp_Amount": order_data['total_amount'],  # Đã chuyển đổi sang integer
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": str(order_data['order_id']),  # Mã tham chiếu đơn hàng
            "vnp_OrderInfo": f"Thanh toán đơn hàng {order_data['order_id']}",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": vnp_ReturnUrl,
            "vnp_IpAddr": order_data['ip_addr'],  # Địa chỉ IP của người dùng
            "vnp_CreateDate": order_data['created_at'],  # Đã chuyển đổi sang định dạng yyyyMMddHHmmss
            "vnp_BillEmail": order_data['email'],  # Email người dùng
            "vnp_UserID": order_data['user_id'],  # User ID người dùng
        }

        # Sắp xếp tham số theo thứ tự a-z
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)

        # Tạo SecureHash sử dụng HMACSHA512
        hash_data = '&'.join([f"{key}={value}" for key, value in sorted_params])
        vnp_SecureHash = hmac.new(
            vnp_HashSecret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        # Gắn SecureHash vào URL
        payment_url = f"{vnp_Url}?{query_string}&vnp_SecureHash={vnp_SecureHash}"
        return payment_url

@api_view(['GET', 'POST'])
def vnpay(request, user_id, order_id):
    try:
        # Lấy thông tin đơn hàng và kiểm tra user_id
        try:
            order = Order.objects.get(order_id=order_id, user_id=user_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or does not belong to the user"}, status=status.HTTP_404_NOT_FOUND)

        # Khai báo biến order_data trước
        order_data = convert_data_for_vnpay(order)

        if request.method == 'GET':
            # Trả về thông tin đơn hàng để xem trước, sửa lại total_amount và created_at
            return Response(order_data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            # Chỉ cho phép thanh toán nếu trạng thái đơn hàng là "Pending"
            if order.status != "Pending":
                return Response({"error": "Order is not eligible for payment"}, status=status.HTTP_400_BAD_REQUEST)

            # Tạo URL thanh toán với VNPay
            vnpay = VNPay(settings.VNPAY_CONFIG)
            payment_url = vnpay.create_payment_url(order_data)

            # Trả về URL thanh toán
            return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)

    except Exception as e:
        # In ra chi tiết lỗi
        print(f"Error occurred: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def vnpay_return(request):
    try:
        # Lấy các tham số trả về từ VNPay
        vnp_response = request.GET.dict()
        vnp_SecureHash = vnp_response.pop('vnp_SecureHash', None)

        # Tạo lại SecureHash từ các tham số trả về
        sorted_params = sorted(vnp_response.items())
        hash_data = '&'.join([f"{key}={value}" for key, value in sorted_params])
        vnp_HashSecret = settings.VNPAY_CONFIG['vnp_HashSecret']
        secure_hash_check = hmac.new(
            vnp_HashSecret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        # Kiểm tra SecureHash có hợp lệ không
        if secure_hash_check != vnp_SecureHash:
            return Response({"error": "Invalid secure hash"}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra mã phản hồi từ VNPay
        if vnp_response.get('vnp_ResponseCode') == '00':  # Mã phản hồi thành công
            order_id = vnp_response.get('vnp_TxnRef')
            payment = Payment.objects.get(transaction_id=order_id)
            payment.status = 'Completed'
            payment.save()

            # Cập nhật trạng thái đơn hàng
            order = payment.order
            order.status = 'Paid'
            order.save()

            return Response({"success": "Payment successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
