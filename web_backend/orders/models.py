from django.db import models
from users.models import User
from products.models import Product

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, db_column='user_id')  # Đảm bảo trỏ đúng cột

    class Meta:
        managed = False  # Không quản lý bảng này bằng Django
        db_table = 'order'  # Tên bảng trong cơ sở dữ liệu

class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, db_column='order_id')  # Trỏ đến cột `order_id` trong bảng `order`
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, db_column='product_id')  # Trỏ đến cột `product_id` trong bảng `product`

    class Meta:
        managed = False  # Không quản lý bảng này
        db_table = 'order_item'  # Tên bảng trong cơ sở dữ liệu
