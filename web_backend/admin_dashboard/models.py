# from django.db import models
# from web_backend.models import *
#
# class Notification(models.Model):
#     notification_id = models.AutoField(primary_key=True)
#     message = models.TextField()
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey('users.User', on_delete=models.CASCADE, db_column='user_id')  # Đảm bảo sử dụng đúng tên cột
#
#     class Meta:
#         managed = False  # Không quản lý bảng này bằng Django
#         db_table = 'notification'  # Tên bảng trong cơ sở dữ liệu
#
# class UserBrowsingBehavior(models.Model):
#     behavior_id = models.AutoField(primary_key=True)
#     activity_type = models.CharField(max_length=50)
#     interaction_value = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
#     timestamp = models.DateTimeField(blank=True, null=True)
#     product = models.ForeignKey('products.Product', on_delete=models.DO_NOTHING, db_column='product_id')  # Đảm bảo đúng cột
#     user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, db_column='user_id')  # Đảm bảo đúng cột
#
#     class Meta:
#         managed = False  # Không quản lý bảng này bằng Django
#         db_table = 'user_browsing_behavior'  # Tên bảng trong cơ sở dữ liệu
