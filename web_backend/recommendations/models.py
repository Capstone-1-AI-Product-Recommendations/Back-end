from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ProductRecommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', models.DO_NOTHING)
    session_id = models.CharField(max_length=255)
    product = models.ForeignKey('products.Product', models.DO_NOTHING)
    category = models.ForeignKey('products.Category', models.DO_NOTHING, blank=True, null=True)
    recommended_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_recommendation'