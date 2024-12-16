from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from web_backend.models import PurchasedProduct, Order, OrderItem, CartItem, User , ShippingAddress
from .serializers import OrderSerializer, ShippingAddressSerializer
import json
from django.utils import timezone
from django.db import transaction

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
    cart_items.delete()

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


@api_view(['PUT'])
def update_shipping_address(request, user_id):
    try:
        with transaction.atomic():
            address_id = request.data.get('id')
            is_default = request.data.get('is_default', False)
            
            # Get address by id and user_id
            shipping_address = ShippingAddress.objects.get(
                id=address_id, 
                user_id=user_id
            )
            
            # Update address fields
            shipping_address.recipient_name = request.data.get('recipient_name')
            shipping_address.recipient_phone = request.data.get('recipient_phone')
            shipping_address.recipient_address = request.data.get('recipient_address')
            shipping_address.is_default = is_default
            
            # If setting as default, update other addresses
            if is_default:
                ShippingAddress.objects.filter(
                    user_id=user_id
                ).exclude(
                    id=address_id
                ).update(is_default=False)
            
            shipping_address.save()
            
            serializer = ShippingAddressSerializer(shipping_address)
            return Response({
                "message": "Địa chỉ đã được cập nhật thành công",
                "address": serializer.data
            }, status=status.HTTP_200_OK)
            
    except ShippingAddress.DoesNotExist:
        return Response({
            "error": "Không tìm thấy địa chỉ"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": f"Lỗi cập nhật địa chỉ: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
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


@api_view(['GET'])
def get_user_addresses(request, user_id):
    try:
        addresses = ShippingAddress.objects.filter(user__user_id=user_id)
        if not addresses.exists():
            return Response({
                "message": "No shipping addresses found for this user",
                "addresses": []
            }, status=status.HTTP_200_OK)
            
        serializer = ShippingAddressSerializer(addresses, many=True)
        return Response({
            "message": "Success",
            "addresses": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error fetching addresses: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def add_shipping_address(request, user_id):
    try:
        with transaction.atomic():
            # Get user
            user = User.objects.get(user_id=user_id)
            is_default = request.data.get('is_default', False)
            
            # Create new address
            shipping_address = ShippingAddress.objects.create(
                user=user,
                recipient_name=request.data.get('recipient_name'),
                recipient_phone=request.data.get('recipient_phone'),
                recipient_address=request.data.get('recipient_address'),
                is_default=is_default
            )
            
            # If setting as default, update other addresses
            if is_default:
                ShippingAddress.objects.filter(
                    user_id=user_id
                ).exclude(
                    id=shipping_address.id
                ).update(is_default=False)
            
            serializer = ShippingAddressSerializer(shipping_address)
            return Response({
                "message": "Địa chỉ đã được thêm thành công",
                "address": serializer.data
            }, status=status.HTTP_201_CREATED)
            
    except User.DoesNotExist:
        return Response({
            "error": "Không tìm thấy người dùng"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": f"Lỗi thêm địa chỉ: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)