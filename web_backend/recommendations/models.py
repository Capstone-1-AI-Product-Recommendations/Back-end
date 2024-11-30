from django.db import models
from users.models import User
from products.models import Product, Category

class ProductRecommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=255)
    recommended_at = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'product_recommendation'
