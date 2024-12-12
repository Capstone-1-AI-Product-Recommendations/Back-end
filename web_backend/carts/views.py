from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from web_backend.models import Cart, CartItem, Product
from .serializers import CartItemSerializer, CartSerializer
from django.db import transaction
# Create your views here.

# Xem tất cả sản phẩm trong giỏ hàng và tổng số tiền
@api_view(['GET'])
def get_cart(request, user_id):
    try:
        cart = Cart.objects.get(user__user_id=user_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response({"error": "Giỏ hàng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

# Thêm sản phẩm vào giỏ hàng
@api_view(['POST'])
def add_to_cart(request, user_id):
    try:
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))  # Mặc định số lượng là 1 nếu không cung cấp

        if not product_id:
            return Response({"error": "Thiếu product_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():  # Sử dụng transaction để đảm bảo dữ liệu nhất quán
            product = Product.objects.select_for_update().get(product_id=product_id)

            if product.quantity < quantity:
                return Response({"error": "Không đủ số lượng sản phẩm trong kho"}, status=status.HTTP_400_BAD_REQUEST)

            # Giảm số lượng sản phẩm trong kho
            product.quantity -= quantity
            product.save()

            # Lấy hoặc tạo mới giỏ hàng và CartItem
            cart, created = Cart.objects.get_or_create(user_id=user_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            # Đảm bảo cart_item.quantity không phải là None
            if cart_item.quantity is None:
                cart_item.quantity = 0

            # Cập nhật số lượng sản phẩm trong giỏ hàng
            cart_item.quantity += quantity
            cart_item.save()

        return Response({"message": "Sản phẩm đã được thêm vào giỏ hàng"}, status=status.HTTP_201_CREATED)
    except Product.DoesNotExist:
        return Response({"error": "Sản phẩm không tồn tại"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Đã xảy ra lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Cập nhật số lượng sản phẩm trong giỏ hàng
@api_view(['PUT'])
def update_cart_item(request, user_id):
    try:
        cart_item_id = request.data.get('cart_item_id')
        quantity = int(request.data.get('quantity', 0))

        if not cart_item_id:
            return Response({"error": "Thiếu ID sản phẩm trong giỏ hàng"}, status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response({"error": "Số lượng phải lớn hơn 0"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():  
            if not cart_item_id or not quantity:
                return Response({"error": "cart_item_id và quantity là bắt buộc"}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra và lấy sản phẩm trong giỏ hàng
            cart_item = CartItem.objects.select_related('product').get(cart__user__user_id=user_id, cart_item_id=cart_item_id)
            product = cart_item.product

            # Tính toán chênh lệch số lượng
            quantity_difference = quantity - cart_item.quantity

            # Kiểm tra nếu số lượng chênh lệch lớn hơn lượng hàng tồn kho
            if quantity_difference > 0 and product.quantity < quantity_difference:
                return Response({"error": "Không đủ số lượng sản phẩm trong kho"}, status=status.HTTP_400_BAD_REQUEST)

            # Điều chỉnh số lượng trong kho
            product.quantity -= quantity_difference
            product.save()

            # Cập nhật số lượng trong giỏ hàng
            cart_item.quantity = quantity
            cart_item.save()


        return Response({"message": "Số lượng sản phẩm đã được cập nhật"}, status=status.HTTP_200_OK)

    except CartItem.DoesNotExist:
        return Response({"error": "Sản phẩm trong giỏ hàng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"error": "Số lượng phải là số nguyên hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Đã xảy ra lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Xóa một sản phẩm khỏi giỏ hàng
@api_view(['DELETE'])
def remove_from_cart(request, user_id, cart_item_id):
    try:
        with transaction.atomic():
            # Lấy cart_item dựa vào cart_item_id
            cart_item = CartItem.objects.select_related('product').get(cart__user_id=user_id, cart_item_id=cart_item_id)
            product = cart_item.product

            # Hoàn lại số lượng sản phẩm vào kho
            product.quantity += cart_item.quantity
            product.save()

            # Xóa sản phẩm khỏi giỏ hàng
            cart_item.delete()


        return Response({"message": "Sản phẩm đã được xóa khỏi giỏ hàng"}, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({"error": "Sản phẩm không tồn tại trong giỏ hàng"}, status=status.HTTP_404_NOT_FOUND)
    
# Xóa tất cả sản phẩm trong giỏ hàng
@api_view(['DELETE'])
def clear_cart(request, user_id):
    try:
        # Lấy giỏ hàng của người dùng và xóa tất cả sản phẩm
        cart = Cart.objects.get(user__user_id=user_id)
        cart.cartitem_set.all().delete()
        return Response({"message": "Giỏ hàng đã được xóa"}, status=status.HTTP_204_NO_CONTENT)
    except Cart.DoesNotExist:
        return Response({"error": "Giỏ hàng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Đã xảy ra lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

