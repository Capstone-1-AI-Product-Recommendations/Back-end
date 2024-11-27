from django.contrib import admin
from .models import Role, User, Category, Product, Order, OrderItem, Cart, CartItem, Ad, ProductAd, AdView, Notification, Comment, UserBrowsingBehavior, ProductRecommendation
# Register your models here.

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Ad)
admin.site.register(ProductAd)
admin.site.register(AdView)
admin.site.register(Notification)
admin.site.register(Comment)
admin.site.register(UserBrowsingBehavior)
admin.site.register(ProductRecommendation)