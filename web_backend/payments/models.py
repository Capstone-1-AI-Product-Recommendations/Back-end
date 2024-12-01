from django.db import models
from users.models import User
from orders.models import Order

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(unique=True, max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, db_column='order_id')  # Trỏ đến cột `order_id` trong bảng `order`
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, db_column='user_id')  # Trỏ đến cột `user_id` trong bảng `user`

    class Meta:
        managed = False  # Django không quản lý bảng này
        db_table = 'payment'  # Tên bảng trong cơ sở dữ liệu
