from django.db import models
from users.models import User
from products.models import Product

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'notification'


class UserBrowsingBehavior(models.Model):
    behavior_id = models.AutoField(primary_key=True)
    activity_type = models.CharField(max_length=50)
    interaction_value = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'user_browsing_behavior'
