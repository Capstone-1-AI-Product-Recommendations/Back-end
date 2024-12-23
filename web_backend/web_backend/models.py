# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.db.models import Avg
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now


class Ad(models.Model):
    ad_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ad'

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cart'


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    cart = models.ForeignKey('Cart', models.DO_NOTHING)
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
        

class Subcategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True)
    subcategory_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subcategory'

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    comment = models.TextField()
    rating = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
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
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'notification'


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add= True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add= True, blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'order'

class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey('Order', models.DO_NOTHING)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('Order', models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payment'

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    quantity = models.IntegerField()
    subcategory = models.ForeignKey('Subcategory', on_delete=models.SET_NULL, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    color = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    detail_product = models.TextField(blank=True, null=True)
    shop = models.ForeignKey('Shop', on_delete=models.SET_NULL, blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    promotion_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    event_id = models.IntegerField(blank=True, null=True)
    sales_strategy = models.IntegerField(blank=True, null=True)
    review_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product'

    @property
    def ads(self):
        return self.productad_set.all()  # Quan hệ reverse với `ProductAd`

    @property
    def stock_status(self):
        return 'in_stock' if self.quantity > 0 else 'out_of_stock'
    def update_computed_rating(self):
        """
        Tính toán và cập nhật trường `rating` dựa trên rating trung bình từ các comment.
        """
        average_rating = self.comment_set.aggregate(average=Avg('rating')).get('average')
        self.rating = round(average_rating, 1) if average_rating else 0
        self.save()

    @property
    def computed_rating(self):
        """
        Lấy giá trị rating hiện tại (trong trường hợp cần sử dụng ngay).
        """
        if self.rating is None:  # Nếu rating chưa được tính
            self.update_computed_rating()
        return self.rating
    @property
    def update_sales_strategy(self):
        # Tính tổng số lượng bán dựa trên các OrderItem liên quan
        total_sales = OrderItem.objects.filter(product=self).aggregate(Sum('quantity'))['quantity__sum'] or 0

        # Xác định chiến lược dựa trên các ngưỡng số lượng bán ra
        if total_sales >= 100:
            self.sales_strategy = 3  # Bán chạy nhất
        elif total_sales >= 50:
            self.sales_strategy = 2  # Phổ biến
        elif total_sales >= 10:
            self.sales_strategy = 1  # Trung bình
        else:
            self.sales_strategy = 0  # Bán ít

        # Lưu lại chiến lược đã cập nhật
        self.save()

@receiver(pre_save, sender=Product)
def update_is_featured(sender, instance, **kwargs):
    # Kiểm tra các tiêu chí: có giá khuyến mãi hoặc được quảng cáo
    if instance.promotion_price or instance.ads.exists():
        instance.is_featured = True
    else:
        instance.is_featured = False
        
class ProductAd(models.Model):
    product_ad_id = models.AutoField(primary_key=True)
    ad = models.ForeignKey('Ad', models.DO_NOTHING)
    product = models.ForeignKey('Product', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_ad'

class ProductImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    file = models.CharField(max_length=200)
    product = models.ForeignKey('Product', on_delete=models.CASCADE,related_name='images')

    class Meta:
        managed = False
        db_table = 'product_image'

class ProductRecommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=255)
    recommended_at = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)
    product = models.ForeignKey('Product', models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'product_recommendation'
    
class ProductVideo(models.Model):
    id = models.BigAutoField(primary_key=True)
    file = models.CharField(max_length=200)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='videos')

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
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
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
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_bank_account'

class UserBrowsingBehavior(models.Model):
    behavior_id = models.AutoField(primary_key=True)
    activity_type = models.CharField(max_length=50)
    interaction_value = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    product = models.ForeignKey('Product', models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_browsing_behavior'       


class ShippingAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shipping_address')
    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(max_length=20)
    recipient_address = models.TextField()
    is_default = models.BooleanField(default=False)
    
    class Meta:
        managed = False
        db_table = 'shipping_address'

class PurchasedProduct(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    purchased_product_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='sold_products')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='purchased_products')  # Liên kết với đơn hàng
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=15, decimal_places=2)  # Lưu giá sản phẩm tại thời điểm mua
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'purchased_product'

class UserBehavior(models.Model):
    VIEW = 'view'
    ADD_TO_CART = 'add_to_cart'
    PURCHASE = 'purchase'
    SEARCH = 'search'

    ACTION_TYPE_CHOICES = [
        (VIEW, 'View'),
        (ADD_TO_CART, 'Add to Cart'),
        (PURCHASE, 'Purchase'),
        (SEARCH, 'Search'),
    ]

    user_id = models.BigIntegerField(null=True, blank=True)  # user_id BIGINT NULL
    session_id = models.CharField(max_length=255, null=True, blank=True)  # session_id VARCHAR(255) NULL
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)  # action_type ENUM(...)
    product_id = models.IntegerField()  # product_id INT NOT NULL
    quantity = models.IntegerField(default=1)  # quantity INT DEFAULT 1
    search_query = models.TextField(null=True, blank=True)  # search_query TEXT NULL
    created_at = models.DateTimeField(default=now)  # created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    updated_at = models.DateTimeField(auto_now=True)  # updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

    class Meta:
        managed = True
        db_table = 'user_behavior'  # Đặt tên bảng là `user_behavior`
        unique_together = (('user_id', 'session_id', 'product_id', 'action_type'),)  # Thêm unique_together nếu cần

    def __str__(self):
        return f"UserBehavior(user_id={self.user_id}, session_id={self.session_id}, action_type={self.action_type})"