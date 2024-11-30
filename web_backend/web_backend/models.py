# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import re
from django.db import models
from django.forms import ValidationError

def validate_email_format(value):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, value):
        raise ValidationError("Invalid email format.")    
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


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'role'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=100)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    reset_token = models.CharField(max_length=50, blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    role = models.ForeignKey(Role, models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.role:
            self.role = Role.objects.get_or_create(role_name="User")[0]
        super().save(*args, **kwargs)
        if self.role and self.role.role_name == "Seller" and not hasattr(self, 'seller_profile'):
            SellerProfile.objects.get_or_create(user=self)
    class Meta:
        managed = False
        db_table = 'user'


class AdView(models.Model):
    ad_view_id = models.AutoField(primary_key=True)
    viewed_at = models.DateTimeField(blank=True, null=True)
    ad = models.ForeignKey(Ad, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'ad_view'


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cart'


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category'


class Subcategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    subcategory_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subcategory'


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    quantity = models.IntegerField()
    category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    seller = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    subcategory = models.ForeignKey(Subcategory, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product'


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    cart = models.ForeignKey(Cart, models.DO_NOTHING)
    product = models.ForeignKey(Product, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cart_item'


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    comment = models.TextField()
    rating = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'comment'


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    message = models.TextField()
    is_read = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'notification'


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'order'


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(Order, models.DO_NOTHING)
    product = models.ForeignKey(Product, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'order_item'


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(unique=True, max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    order = models.ForeignKey(Order, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payment'


class ProductAd(models.Model):
    product_ad_id = models.AutoField(primary_key=True)
    ad = models.ForeignKey(Ad, models.DO_NOTHING)
    product = models.ForeignKey(Product, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_ad'


class ProductImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    file = models.CharField(max_length=200)
    product = models.ForeignKey(Product, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_image'


class ProductRecommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=255)
    recommended_at = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_recommendation'


class ProductVideo(models.Model):
    id = models.BigAutoField(primary_key=True)
    file = models.CharField(max_length=200)
    product = models.ForeignKey(Product, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_video'


class SellerProfile(models.Model):
    seller_id = models.CharField(primary_key=True, max_length=50)
    store_name = models.CharField(max_length=255, blank=True, null=True)
    store_address = models.TextField(blank=True, null=True)
    user = models.OneToOneField(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'seller_profile'


class Shop(models.Model):
    shop_id = models.AutoField(primary_key=True)
    shop_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shop'


class ShopInfo(models.Model):
    shop_info_id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, models.DO_NOTHING, blank=True, null=True)
    product_count = models.IntegerField(blank=True, null=True)
    followers_count = models.IntegerField(blank=True, null=True)
    is_following = models.IntegerField(blank=True, null=True)
    join_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shop_info'


class UserBankAccount(models.Model):
    bank_account_id = models.AutoField(primary_key=True)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_holder_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_bank_account'


class UserBrowsingBehavior(models.Model):
    behavior_id = models.AutoField(primary_key=True)
    activity_type = models.CharField(max_length=50)
    interaction_value = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_browsing_behavior'
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.product.name if self.product else 'Unknown Product'}"
