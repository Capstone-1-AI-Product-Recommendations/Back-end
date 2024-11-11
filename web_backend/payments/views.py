from time import time
import uuid
import json
import hmac
import hashlib
from datetime import datetime
import requests
from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from web_backend.models import Payment, Order
from .serializer import PaymentSerializer
from django.utils import timezone
# Create your views here.

config = {
    "appid": 554,  # App ID của bạn trên ZaloPay
    "key1": "8NdU5pG5R2spGHGhyO99HN1OhD8IQJBn",  # Key1 của bạn
    "key2": "uUfsWgfLkRLzq6W2uNXTCxrfxs51auny",  # Key2 của bạn
    "endpoint": "https://sandbox.zalopay.com.vn/v001/tpe/createorder"  # Endpoint của ZaloPay (sandbox)
}

# Thanh toán khi nhận hàng (COD)
@csrf_exempt
@api_view(['POST'])
def cod_payment(request, order_id):
    """ API thanh toán khi nhận hàng (Cash on Delivery) """
    try:
        order = get_object_or_404(Order, order_id=order_id)

        if order.status != 'PENDING':
            return Response({"message": "Order is not in pending status."}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo bản ghi thanh toán khi nhận hàng
        payment = Payment.objects.create(
            user=order.user,
            order=order,
            amount=order.total,
            status='COMPLETED',
            payment_method="Cash on Delivery",
            transaction_id=f"CASH_{timezone.now().strftime('%Y%m%d%H%M%S')}",
        )

        # Cập nhật trạng thái đơn hàng
        order.status = 'COMPLETED'
        order.save()

        # Dùng serializer để trả về thông tin Payment
        payment_serializer = PaymentSerializer(payment)
        return Response(payment_serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Thanh toán qua ZaloPay
@csrf_exempt
@api_view(['POST'])
def zalopay_payment(request):
    try:
        # Lấy số tiền thanh toán từ request
        amount = request.data.get('amount')  # Người dùng nhập số tiền
        user_id = request.data.get('user_id')  # ID người dùng
        order_id = request.data.get('order_id')  # ID đơn hàng (nếu có)

        # Kiểm tra nếu không có thông tin cần thiết
        if not amount or not user_id:
            return Response({"error": "Thiếu thông tin thanh toán"}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra nếu đơn hàng có tồn tại không
        order = Order.objects.filter(order_id=order_id).first()
        if order is None:
            return Response({"error": "Đơn hàng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        # Tạo thông tin thanh toán
        apptransid = "{:%y%m%d}_{}".format(timezone.now(), uuid.uuid4())
        apptime = int(round(time() * 1000))
        
        # Tạo dữ liệu thanh toán cho ZaloPay
        data = {
            "appid": config["appid"],
            "apptransid": apptransid,
            "appuser": str(user_id),
            "apptime": apptime,
            "amount": amount * 100,  # Chuyển đổi sang đơn vị đồng
            "description": f"Thanh toán cho đơn hàng {order_id}",
            "bankcode": "zalopayapp",
            "item": json.dumps([
                { "itemid": f"item{order.order_id}", "itemname": f"Order {order.order_id}", "itemprice": float(amount), "itemquantity": 1 }
            ]),
            "embeddata": json.dumps({"merchantinfo": "embeddata123"})
        }

        # Tính toán giá trị mac
        mac_data = "{}|{}|{}|{}|{}|{}|{}".format(data["appid"], data["apptransid"], data["appuser"],
                                                  data["amount"], data["apptime"], data["embeddata"], data["item"])
        data["mac"] = hmac.new(config['key1'].encode(), mac_data.encode(), hashlib.sha256).hexdigest()

        # Gửi yêu cầu thanh toán đến ZaloPay
        response = requests.post(config["endpoint"], data=data)
        result = response.json()

        # Kiểm tra kết quả từ ZaloPay
        if result.get("returncode") == 1:
            # Lưu thông tin thanh toán vào database
            payment = Payment(
                user_id=user_id,
                order_id=order_id,
                amount=amount,
                status='PENDING',  # Trạng thái chờ xử lý ban đầu
                payment_method='ZaloPay',
                transaction_id=data["apptransid"]
            )
            payment.save()

            return Response({"order_url": result.get("orderurl")}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Lỗi khi tạo đơn thanh toán"}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def payment_callback(request):
    try:
        # Lấy dữ liệu callback từ ZaloPay
        cbdata = request.data
        mac = hmac.new(config['key2'].encode(), cbdata['data'].encode(), hashlib.sha256).hexdigest()

        # Kiểm tra tính hợp lệ của callback
        if mac != cbdata['mac']:
            return Response({"returncode": -1, "returnmessage": "mac không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)

        # Cập nhật trạng thái thanh toán vào bảng Payment
        dataJson = json.loads(cbdata['data'])
        transaction_id = dataJson.get('apptransid')
        status = dataJson.get('status')  # Trạng thái thanh toán (1: Thành công, 0: Thất bại)

        payment = Payment.objects.get(transaction_id=transaction_id)

        if status == '1':
            payment.status = 'COMPLETED'  # Thành công
        else:
            payment.status = 'FAILED'  # Thất bại

        payment.save()

        return Response({"returncode": 1, "returnmessage": "success"}, status=status.HTTP_200_OK)
    except Payment.DoesNotExist:
        return Response({"error": "Thanh toán không tồn tại"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
