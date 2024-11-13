from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from web_backend.models import Cart, CartItem, Product
from .serializer import CartItemSerializer, CartSerializer
# Create your views here.

# Xem tất cả sản phẩm trong giỏ hàng và tổng số tiền
@api_view(['GET'])
def get_cart(request, user_id):
    try:
        cart = Cart.objects.get(user__user_id=user_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response({"error": "Giỏ hàng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

# Thêm sản phẩm vào giỏ hàng
@api_view(['POST'])
def add_to_cart(request, user_id):
    try:
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        # Kiểm tra sản phẩm tồn tại
        product = Product.objects.get(product_id=product_id)
        # Lấy giỏ hàng của người dùng hoặc tạo mới nếu chưa có
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        # Cập nhật số lượng nếu sản phẩm đã có trong giỏ
        cart_item.quantity = quantity
        cart_item.save()
        return Response({"message": "Sản phẩm đã được thêm vào giỏ hàng"}, status=status.HTTP_201_CREATED)
    except Product.DoesNotExist:
        return Response({"error": "Sản phẩm không tồn tại"}, status=status.HTTP_400_BAD_REQUEST)

# Cập nhật số lượng sản phẩm trong giỏ hàng
@api_view(['PUT'])
def update_cart_item(request, user_id):
    try:
        cart_item_id = request.data.get('cart_item_id')
        quantity = request.data.get('quantity')
        # Lấy sản phẩm trong giỏ hàng
        cart_item = CartItem.objects.get(cart__user__user_id=user_id, cart_item_id=cart_item_id)
        cart_item.quantity = quantity
        cart_item.save()
        return Response({"message": "Số lượng sản phẩm đã được cập nhật"}, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({"error": "Sản phẩm trong giỏ hàng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

# Xóa một sản phẩm khỏi giỏ hàng
@api_view(['DELETE'])
def remove_from_cart(request, cart_item_id):
    try:
        # Lấy sản phẩm trong giỏ hàng và xóa
        cart_item = CartItem.objects.get(cart_item_id=cart_item_id)
        cart_item.delete()  # Xóa sản phẩm khỏi giỏ
        return Response({"message": "Sản phẩm đã được xóa khỏi giỏ hàng"}, status=status.HTTP_204_NO_CONTENT)
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