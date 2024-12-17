from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from web_backend.models import PurchasedProduct, Order, OrderItem, CartItem, User , ShippingAddress
from .serializers import OrderSerializer, ShippingAddressSerializer
import json
from django.utils import timezone

@api_view(['GET'])
def get_orders(request, user_id, order_id=None):
    try:
        # Kiểm tra user_id hợp lệ
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if order_id:
        # Lấy order cụ thể dựa trên order_id và user
        try:
            order = Order.objects.get(
                order_id=order_id,
                orderitem__product__shop__user=user
            )
        except Order.DoesNotExist:
            return Response({"detail": "Order not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    # Lấy tất cả các đơn hàng của user nếu không có order_id
    orders = Order.objects.filter(orderitem__product__shop__user=user).distinct()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_order(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Lấy cart_item_ids và chuyển chuỗi JSON thành danh sách
    cart_item_ids_str = request.data.get('cart_item_ids', '[]')  # Mặc định là chuỗi rỗng nếu không có
    try:
        cart_item_ids = json.loads(cart_item_ids_str)  # Chuyển chuỗi JSON thành danh sách
    except json.JSONDecodeError:
        return Response({"error": "Dữ liệu cart_item_ids không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)

    if not cart_item_ids:
        return Response({"error": "Cần phải chọn ít nhất một sản phẩm."}, status=status.HTTP_400_BAD_REQUEST)

    cart_items = CartItem.objects.filter(cart_item_id__in=cart_item_ids, cart__user=user)
    if not cart_items.exists():
        return Response({"error": "Không tìm thấy sản phẩm trong giỏ hàng."}, status=status.HTTP_404_NOT_FOUND)

    # Tiến hành tạo đơn hàng
    order = Order.objects.create(
        user=user,
        total=0,
        status='Chờ xác nhận',
    )

    total_amount = 0
    for item in cart_items:
        product = item.product
        quantity = item.quantity
        price = product.price
        total_amount += price * quantity

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price * quantity,
        )
        # Lưu thông tin xuống PurchasedProduct
        PurchasedProduct.objects.create(
            user=user,
            product=product,
            shop=product.shop,  # Giả định mỗi sản phẩm liên kết với shop qua `product.shop`
            order=order,
            quantity=quantity,
            price_at_purchase=price,
            status='Chờ xác nhận',  # Mặc định trạng thái ban đầu là `completed`
            purchased_at=timezone.now(),  # Ngày giờ mua
        )

    order.total = total_amount
    order.save()

    # Xử lý thông tin nhận hàng
    recipient_name = request.data.get('recipient_name', user.full_name) or user.full_name
    recipient_phone = request.data.get('recipient_phone', user.phone_number) or user.phone_number
    recipient_address = request.data.get('recipient_address', user.address) or user.address

    # Cập nhật hoặc tạo mới địa chỉ nhận hàng
    shipping_address, created = ShippingAddress.objects.update_or_create(
        user=user,
        defaults={
            'recipient_name': recipient_name,
            'recipient_phone': recipient_phone,
            'recipient_address': recipient_address,
        }
    )

    # Trả về thông tin đơn hàng
    order_serializer = OrderSerializer(order)
    return Response(order_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT'])
def update_shipping_address(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        try:
            # Lấy thông tin từ bảng ShippingAddress
            shipping_address = user.shipping_address
        except ShippingAddress.DoesNotExist:
            # Nếu không có, tạo một ShippingAddress tạm thời từ thông tin User
            shipping_address = ShippingAddress(
                recipient_name=user.full_name,
                recipient_phone=user.phone_number,
                recipient_address=user.address
            )
        serializer = ShippingAddressSerializer(shipping_address)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Cập nhật hoặc tạo thông tin nhận hàng
        shipping_address, created = ShippingAddress.objects.get_or_create(user=user)
        shipping_address.recipient_name = request.data.get('recipient_name', shipping_address.recipient_name or user.full_name)
        shipping_address.recipient_phone = request.data.get('recipient_phone', shipping_address.recipient_phone or user.phone_number)
        shipping_address.recipient_address = request.data.get('recipient_address', shipping_address.recipient_address or user.address)
        shipping_address.save()

        return Response({"message": "Thông tin nhận hàng đã được cập nhật thành công."}, status=status.HTTP_200_OK)

    
@api_view(['DELETE'])
def cancel_order_item(request, user_id, order_item_id):
    try:
        # Lấy thông tin người dùng
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Lấy OrderItem từ ID và đảm bảo nó thuộc đơn hàng của người dùng
        order_item = OrderItem.objects.get(order_item_id=order_item_id, order__user=user)
    except OrderItem.DoesNotExist:
        return Response({"error": "Order item not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy đơn hàng từ OrderItem để kiểm tra trạng thái
    order = order_item.order

    # Kiểm tra nếu đơn hàng đã hủy hoặc đã giao
    if order.status in ['Đã hủy', 'Đã giao', 'Đã xác nhận']:
        return Response({"error": f"Không thể hủy sản phẩm trong đơn hàng đã ở trạng thái '{order.status}'."}, status=status.HTTP_400_BAD_REQUEST)

    # Cập nhật số lượng sản phẩm trong Product
    product = order_item.product

    # Tăng lại số lượng sản phẩm trong kho
    product.quantity += order_item.quantity
    product.save()
    # Cập nhật tổng tiền của đơn hàng (trừ đi số tiền của OrderItem bị xóa)
    order.total -= order_item.price 
    order.save()
    # Xóa OrderItem khỏi đơn hàng
    order_item.delete()
    # Kiểm tra xem đơn hàng còn sản phẩm nào không, nếu không có thì hủy đơn hàng
    if not order.orderitem_set.exists():
        order.status = 'Đã hủy'  # Nếu không còn sản phẩm, hủy đơn hàng
        order.save()

    return Response({"message": "Đơn hàng đã được hủy."}, status=status.HTTP_200_OK)