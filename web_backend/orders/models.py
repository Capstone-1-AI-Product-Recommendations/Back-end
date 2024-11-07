from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', models.DO_NOTHING)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order'

class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Order', models.DO_NOTHING)
    product = models.ForeignKey('products.Product', models.DO_NOTHING)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'order_item'

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cart'

class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey('Cart', models.DO_NOTHING)
    product = models.ForeignKey('products.Product', models.DO_NOTHING)
    quantity = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cart_item'