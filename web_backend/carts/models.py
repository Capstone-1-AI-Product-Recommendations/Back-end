# from django.db import models
# # from users.models import User
# # from products.models import Product
# from web_backend.models import *
#
# class Cart(models.Model):
#     cart_id = models.AutoField(primary_key=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     user = models.ForeignKey('users.User', on_delete=models.CASCADE, db_column='user_id')  # Đảm bảo trỏ đúng cột trong DB
#
#     class Meta:
#         managed = False  # Không quản lý bảng này
#         db_table = 'cart'  # Tên bảng trong cơ sở dữ liệu
#
# class CartItem(models.Model):
#     cart_item_id = models.AutoField(primary_key=True)
#     quantity = models.IntegerField(blank=True, null=True)
#     added_at = models.DateTimeField(auto_now_add=True)
#     cart = models.ForeignKey('Cart', on_delete=models.CASCADE, db_column='cart_id')  # Trỏ đến cột `cart_id` trong bảng `cart`
#     product = models.ForeignKey('products.Product', on_delete=models.CASCADE, db_column='product_id')  # Trỏ đến cột `product_id` trong bảng `product`
#
#     class Meta:
#         managed = False  # Không quản lý bảng này
#         db_table = 'cart_item'  # Tên bảng trong cơ sở dữ liệu
