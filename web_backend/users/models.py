from django.db import models

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'role'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=255)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'user'


class UserBankAccount(models.Model):
    account_id = models.AutoField(primary_key=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'user_bank_account'
