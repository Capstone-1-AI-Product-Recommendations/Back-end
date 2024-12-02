from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from web_backend.models import Order, OrderItem, CartItem, ShippingAddress, User
from .serializers import OrderSerializer, ShippingAddressSerializer

@api_view(['GET', 'POST'])
def create_order(request, user_id):
    # Lấy thông tin người dùng
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Lấy thông tin nhận hàng từ bảng ShippingAddress nếu có, hoặc thông tin mặc định từ bảng User
        try:
            shipping_address = user.shipping_address
        except ShippingAddress.DoesNotExist:
            # Nếu không có thông tin nhận hàng, lấy thông tin mặc định từ bảng User
            shipping_address = ShippingAddress(
                recipient_name=user.full_name,
                recipient_phone=user.phone_number,
                recipient_address=user.address
            )

        # Sử dụng serializer để trả về thông tin nhận hàng
        serializer = ShippingAddressSerializer(shipping_address)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Lấy danh sách cart_item_ids từ yêu cầu
        cart_item_ids = request.data.get('cart_item_ids', [])
        if not cart_item_ids:
            return Response({"error": "Cần phải chọn ít nhất một sản phẩm."}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra sự tồn tại của CartItems và tạo đơn hàng
        cart_items = CartItem.objects.filter(cart_item_id__in=cart_item_ids, cart__user=user)
        if not cart_items.exists():
            return Response({"error": "Không tìm thấy sản phẩm trong giỏ hàng."}, status=status.HTTP_404_NOT_FOUND)

        # Tạo đơn hàng mới
        order = Order.objects.create(
            user=user,
            total=0,  # Tổng tiền sẽ được tính sau
            status='Pending',
        )

        total_amount = 0
        for item in cart_items:
            product = item.product
            quantity = item.quantity
            price = product.price
            total_amount += price * quantity

            # Tạo OrderItem cho mỗi sản phẩm trong đơn hàng
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price = price * quantity,
            )

        # Cập nhật tổng tiền của đơn hàng
        order.total = total_amount
        order.save()

        # Xóa các CartItem sau khi tạo OrderItem
        cart_items.delete()

        # Thông tin nhận hàng (có thể thay đổi)
        recipient_name = request.data.get('recipient_name', user.full_name)
        recipient_phone = request.data.get('recipient_phone', user.phone_number)
        recipient_address = request.data.get('recipient_address', user.address)

        # Tạo hoặc cập nhật thông tin nhận hàng trong bảng ShippingAddress
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
    
@api_view(['PUT'])
def update_shipping_address(request, user_id):
    # Lấy thông tin người dùng
    user = User.objects.get(user_id=user_id)
    # Lấy thông tin nhận hàng của người dùng
    shipping_address = ShippingAddress.objects.filter(user=user).first()
    if not shipping_address:
        return Response({"error": "Thông tin nhận hàng không tồn tại."}, status=status.HTTP_400_BAD_REQUEST)
    # Cập nhật thông tin nhận hàng
    shipping_address.recipient_name = request.data.get('recipient_name', shipping_address.recipient_name)
    shipping_address.recipient_phone = request.data.get('recipient_phone', shipping_address.recipient_phone)
    shipping_address.recipient_address = request.data.get('recipient_address', shipping_address.recipient_address)
    # Lưu thông tin nhận hàng đã cập nhật
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
    if order.status in ['Canceled', 'Delivered', 'Confirmed']:
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
        order.status = 'Canceled'  # Nếu không còn sản phẩm, hủy đơn hàng
        order.save()

    return Response({"message": "Đơn hàng đã được hủy."}, status=status.HTTP_200_OK)