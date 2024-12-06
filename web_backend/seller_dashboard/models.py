# from django.db import models
# from users.models import User
#
#
# class Ad(models.Model):
#     ad_id = models.AutoField(primary_key=True)  # ID quảng cáo
#     title = models.CharField(max_length=255)  # Tiêu đề
#     description = models.TextField(blank=True, null=True)  # Mô tả quảng cáo
#     discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Phần trăm giảm giá
#     start_date = models.DateField()  # Ngày bắt đầu
#     end_date = models.DateField()  # Ngày kết thúc
#     created_at = models.DateTimeField(auto_now_add=True)  # Thời gian tạo
#     updated_at = models.DateTimeField(auto_now=True)  # Thời gian cập nhật
#
#     class Meta:
#         managed = False  # Django không quản lý bảng này
#         db_table = 'ad'  # Tên bảng trong cơ sở dữ liệu
#
#
# class SellerProfile(models.Model):
#     seller_id = models.CharField(primary_key=True, max_length=50)  # ID người bán
#     store_name = models.CharField(max_length=255, blank=True, null=True)  # Tên cửa hàng
#     store_address = models.TextField(blank=True, null=True)  # Địa chỉ chi tiết của cửa hàng
#     user = models.OneToOneField('users.User', on_delete=models.DO_NOTHING)  # Liên kết với bảng User
#     city = models.CharField(max_length=100, blank=True, null=True)  # Thành phố của cửa hàng
#     province = models.CharField(max_length=100, blank=True, null=True)  # Tỉnh/Thành phố của cửa hàng
#
#     class Meta:
#         managed = False  # Django không quản lý bảng này
#         db_table = 'seller_profile'  # Tên bảng trong cơ sở dữ liệu
#
#
#
# class Shop(models.Model):
#     shop_id = models.AutoField(primary_key=True)  # ID cửa hàng
#     shop_name = models.CharField(max_length=255)  # Tên cửa hàng
#     user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, blank=True, null=True)  # Liên kết với bảng User
#
#     class Meta:
#         managed = False  # Django không quản lý bảng này
#         db_table = 'shop'  # Tên bảng trong cơ sở dữ liệu
#
#
# class ShopInfo(models.Model):
#     shop_info_id = models.AutoField(primary_key=True)  # ID thông tin cửa hàng
#     shop = models.ForeignKey(Shop, on_delete=models.DO_NOTHING, blank=True, null=True)  # Liên kết với bảng Shop
#     product_count = models.IntegerField(blank=True, null=True)  # Số lượng sản phẩm
#     followers_count = models.IntegerField(blank=True, null=True)  # Số lượng người theo dõi
#     is_following = models.IntegerField(blank=True, null=True)  # Trạng thái theo dõi
#     join_date = models.DateTimeField(blank=True, null=True)  # Ngày tham gia
#
#     class Meta:
#         managed = False  # Django không quản lý bảng này
#         db_table = 'shop_info'  # Tên bảng trong cơ sở dữ liệu
