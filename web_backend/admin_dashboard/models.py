from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', models.DO_NOTHING)
    message = models.TextField()
    is_read = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notification'

class UserBrowsingBehavior(models.Model):
    behavior_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    product = models.ForeignKey('products.Product', models.DO_NOTHING)
    activity_type = models.CharField(max_length=50)
    interaction_value = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_browsing_behavior'