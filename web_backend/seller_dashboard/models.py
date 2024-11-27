from django.db import models
from web_backend.models import Product, Order, OrderItem, Ad, ProductAd, SellerProfile, Notification, Comment, ProductRecommendation
from django.contrib.auth.models import User
# Create your models here.
class ProductAd(models.Model):
    product_ad_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('products.Product', models.DO_NOTHING)
    ad = models.ForeignKey('Ad', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_ad'

class Ad(models.Model):
    ad_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ad'

class AdView(models.Model):
    ad_view_id = models.AutoField(primary_key=True)
    ad = models.ForeignKey('Ad', models.DO_NOTHING)
    user = models.ForeignKey('users.User', models.DO_NOTHING)
    viewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ad_view'