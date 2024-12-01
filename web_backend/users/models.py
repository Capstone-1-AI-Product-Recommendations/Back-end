from django.db import models

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)  # ID vai trò
    role_name = models.CharField(max_length=50)  # Tên vai trò

    class Meta:
        managed = False  # Django không quản lý bảng này
        db_table = 'role'  # Tên bảng trong cơ sở dữ liệu


class User(models.Model):
    user_id = models.AutoField(primary_key=True)  # ID người dùng
    username = models.CharField(unique=True, max_length=100)  # Tên đăng nhập, duy nhất
    password = models.CharField(max_length=100)  # Mật khẩu
    email = models.CharField(unique=True, max_length=255)  # Email, duy nhất
    role = models.ForeignKey('Role', on_delete=models.DO_NOTHING)  # Liên kết với bảng Role

    class Meta:
        managed = False  # Django không quản lý bảng này
        db_table = 'user'  # Tên bảng trong cơ sở dữ liệu


class UserBankAccount(models.Model):
    account_id = models.AutoField(primary_key=True)  # ID tài khoản ngân hàng
    account_number = models.CharField(max_length=50, blank=True, null=True)  # Số tài khoản ngân hàng
    bank_name = models.CharField(max_length=100, blank=True, null=True)  # Tên ngân hàng
    user = models.ForeignKey('User', on_delete=models.DO_NOTHING, blank=True, null=True)  # Liên kết với bảng User

    class Meta:
        managed = False  # Django không quản lý bảng này
        db_table = 'user_bank_account'  # Tên bảng trong cơ sở dữ liệu
