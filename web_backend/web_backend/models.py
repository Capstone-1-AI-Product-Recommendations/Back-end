# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


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

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cart'


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    cart = models.ForeignKey(Cart, models.DO_NOTHING)
    product = models.ForeignKey('Product', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cart_item'


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category'


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    comment = models.TextField()
    rating = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    product = models.ForeignKey('Product', models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'comment'


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    message = models.TextField()
    is_read = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'notification'


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'order'


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(Order, models.DO_NOTHING)
    product = models.ForeignKey('Product', models.DO_NOTHING)

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
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payment'

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    quantity = models.IntegerField()
    subcategory = models.ForeignKey('Subcategory', models.DO_NOTHING, blank=True, null=True)
    is_featured = models.BooleanField(default=False)  # Sửa thành BooleanField
    color = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    shop = models.ForeignKey('Shop', models.DO_NOTHING, blank=True, null=True)
    promotion_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Thêm trường này
    event_id = models.IntegerField(blank=True, null=True)  # Thêm trường này

    class Meta:
        managed = False
        db_table = 'product'

    @property
    def ads(self):
        return self.productad_set.all()  # Quan hệ reverse với `ProductAd`

    @property
    def stock_status(self):
        return 'in_stock' if self.quantity > 0 else 'out_of_stock'
    @property
    def computed_rating(self):
        """
        Tính rating trung bình từ các comment.
        """
        average_rating = self.comment_set.aggregate(average=Avg('rating')).get('average')
        return round(average_rating, 1) if average_rating else 0

from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Product)
def update_is_featured(sender, instance, **kwargs):
    # Kiểm tra các tiêu chí: có giá khuyến mãi, thuộc sự kiện, hoặc được quảng cáo
    if instance.promotion_price or instance.event_id or instance.ads.exists():
        instance.is_featured = True
    else:
        instance.is_featured = False

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
    category_id = models.IntegerField(blank=True, null=True)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)

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


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'role'


class SellerProfile(models.Model):
    seller_id = models.CharField(primary_key=True, max_length=50)
    store_name = models.CharField(max_length=255, blank=True, null=True)
    store_address = models.TextField(blank=True, null=True)
    user = models.OneToOneField('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'seller_profile'


class Shop(models.Model):
    shop_id = models.AutoField(primary_key=True)
    shop_name = models.CharField(max_length=255)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

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


class Subcategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    subcategory_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subcategory'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    reset_token = models.CharField(max_length=50, blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    role = models.ForeignKey(Role, models.DO_NOTHING, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'


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
