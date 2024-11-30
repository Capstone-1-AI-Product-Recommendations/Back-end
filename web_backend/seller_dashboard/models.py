from django.db import models
from users.models import User

class Ad(models.Model):
    ad_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ad'


class AdView(models.Model):
    ad_view_id = models.AutoField(primary_key=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ad_view'


class SellerProfile(models.Model):
    seller_id = models.CharField(primary_key=True, max_length=50)
    store_name = models.CharField(max_length=255, blank=True, null=True)
    store_address = models.TextField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'seller_profile'


class Shop(models.Model):
    shop_id = models.AutoField(primary_key=True)
    shop_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'shop'


class ShopInfo(models.Model):
    shop_info_id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, on_delete=models.DO_NOTHING, blank=True, null=True)
    product_count = models.IntegerField(blank=True, null=True)
    followers_count = models.IntegerField(blank=True, null=True)
    is_following = models.IntegerField(blank=True, null=True)
    join_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'shop_info'
