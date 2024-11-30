from django.db import models
from users.models import User
from products.models import Product

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart'


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    quantity = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart_item'
