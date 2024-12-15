# from django.db import models
# from users.models import User
# from products.models import Product, Category
#
#
# class ProductRecommendation(models.Model):
#     recommendation_id = models.AutoField(primary_key=True)  # ID tự động
#     session_id = models.CharField(max_length=255)  # ID phiên người dùng
#     recommended_at = models.DateTimeField(blank=True, null=True)  # Thời gian khuyến nghị
#     description = models.TextField(blank=True, null=True)  # Mô tả sản phẩm được khuyến nghị
#     category = models.ForeignKey('products.Category', on_delete=models.DO_NOTHING, blank=True, null=True, db_column='category_id')  # Liên kết với bảng Category
#     product = models.ForeignKey('products.Product', on_delete=models.DO_NOTHING, db_column='product_id')  # Liên kết với bảng Product
#     user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, db_column='user_id')  # Liên kết với bảng User
#
#     class Meta:
#         managed = False  # Django không quản lý bảng này
#         db_table = 'product_recommendation'  # Tên bảng trong cơ sở dữ liệu
