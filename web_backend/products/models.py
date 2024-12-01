from django.db import models
from users.models import User
from seller_dashboard.models import SellerProfile


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  # Django không quản lý bảng này
        db_table = 'category'  # Tên bảng trong cơ sở dữ liệu


class Subcategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    subcategory_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True, db_column='category_id')

    class Meta:
        managed = False
        db_table = 'subcategory'


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True, db_column='category_id')
    subcategory = models.ForeignKey('Subcategory', on_delete=models.CASCADE, blank=True, null=True, db_column='subcategory_id')
    seller = models.ForeignKey('seller_dashboard.SellerProfile', on_delete=models.CASCADE, blank=True, null=True, db_column='seller_id')
    color = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    IN_STOCK = 'in_stock'
    OUT_OF_STOCK = 'out_of_stock'
    STOCK_STATUS_CHOICES = [
        (IN_STOCK, 'In Stock'),
        (OUT_OF_STOCK, 'Out of Stock'),
    ]

    class Meta:
        managed = False
        db_table = 'product'


class ProductAd(models.Model):
    product_ad_id = models.AutoField(primary_key=True)
    ad = models.ForeignKey('seller_dashboard.Ad', on_delete=models.DO_NOTHING, db_column='ad_id')
    product = models.ForeignKey('Product', on_delete=models.DO_NOTHING, db_column='product_id')

    class Meta:
        managed = False
        db_table = 'product_ad'


class ProductImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    file = models.CharField(max_length=200)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='product_id')

    class Meta:
        managed = False
        db_table = 'product_image'


class ProductVideo(models.Model):
    id = models.BigAutoField(primary_key=True)
    file = models.CharField(max_length=200)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='product_id')

    class Meta:
        managed = False
        db_table = 'product_video'


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    comment = models.TextField()
    rating = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    product = models.ForeignKey('Product', on_delete=models.DO_NOTHING, db_column='product_id')
    user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, db_column='user_id')

    class Meta:
        managed = False
        db_table = 'comment'
