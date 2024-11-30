from django.utils.timezone import now
from .models import UserBrowsingBehavior, Product

class UserActivityLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            user = request.user
            
            # Log 'View Product' activity
            if 'product' in request.path:
                product_id = request.GET.get('product_id')
                if product_id:
                    try:
                        product = Product.objects.get(id=product_id)
                        UserBrowsingBehavior.objects.create(
                            user=user,
                            product=product,
                            activity_type='viewed_product',
                            interaction_value=1.0,
                            timestamp=now(),
                        )
                    except Product.DoesNotExist:
                        pass

            # Log 'Add to Cart' activity
            if 'cart' in request.path and request.method == 'POST':
                product_id = request.POST.get('product_id')
                try:
                    product = Product.objects.get(id=product_id)
                    UserBrowsingBehavior.objects.create(
                        user=user,
                        product=product,
                        activity_type='added_to_cart',
                        interaction_value=1.0,
                        timestamp=now(),
                    )
                except Product.DoesNotExist:
                    pass

        return response
