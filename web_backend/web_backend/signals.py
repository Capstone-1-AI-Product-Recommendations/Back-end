from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserBrowsingBehavior, CartItem
from django.utils.timezone import now

@receiver(post_save, sender=CartItem)
def log_add_to_cart(sender, instance, created, **kwargs):
    if created:  # Nếu là sản phẩm mới được thêm vào giỏ hàng
        UserBrowsingBehavior.objects.create(
            user=instance.cart.user,
            product=instance.product,
            activity_type='added_to_cart',
            interaction_value=1.0,
            timestamp=now(),
        )
