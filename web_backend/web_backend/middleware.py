import logging
from django.utils.timezone import now
from django.utils import timezone
from django.http import JsonResponse
from web_backend.models import UserBrowsingBehavior, Product, User

logger = logging.getLogger(__name__)

class UserActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Middleware logic before view is called
        response = self.get_response(request)

        # Process after view function is executed
        self.handle_viewed_product(request)
        self.handle_searched_product(request)
        self.handle_added_to_cart(request)

        return response

    def handle_viewed_product(self, request):
        """Handle logging when user views a product."""
        if request.method == 'GET' and 'products/detail' in request.path:
            # Extract user_id and product_id from URL kwargs
            user_id = request.resolver_match.kwargs.get('user_id')
            product_id = request.resolver_match.kwargs.get('product_id')

            if user_id and product_id:
                try:
                    user = User.objects.get(user_id=user_id)
                    product = Product.objects.get(product_id=product_id)

                    # Log viewing activity
                    UserBrowsingBehavior.objects.create(
                        user=user,
                        product=product,
                        activity_type='viewed_product',
                        interaction_value=1.0,
                        timestamp=now(),
                        content=f"{product.name}"
                    )
                    logger.info(f"User {user.username} viewed product {product.name}")

                except User.DoesNotExist:
                    logger.error(f"User with ID {user_id} does not exist")
                except Product.DoesNotExist:
                    logger.error(f"Product with ID {product_id} does not exist")

    def handle_searched_product(self, request):
        """Handle logging when user performs a search."""
        if request.method == 'GET' and 'search_products/' in request.path:
            try:
                search_term = request.GET.get('search_products', '').strip()
                if not search_term:
                    logger.info("Search term is empty. Skipping behavior tracking.")
                    return

                # Check for user_id in cookies
                user_id = request.COOKIES.get('user_id')
                user = None

                if user_id:
                    user = User.objects.filter(user_id=user_id).first()
                    if not user:
                        logger.warning("Invalid user_id in cookie. Creating new guest user.")
                else:
                    logger.info("No user_id in cookies. Creating new guest user.")

                # Create guest user if no valid user exists
                if not user:
                    user = User.objects.create(
                        username=f"Guest_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                        email=f"guest_{timezone.now().strftime('%Y%m%d%H%M%S')}@example.com"
                    )

                # Add user_id to cookies for future requests
                request.new_user_id = user.user_id

                # Log search behavior
                UserBrowsingBehavior.objects.create(
                    user=user,
                    product=None,
                    activity_type='searched_product',
                    interaction_value=1.0,
                    timestamp=timezone.now(),
                    content=f"Search Term: {search_term}"
                )
                logger.info(f"Search behavior saved: User - {user.username}, Search Term - {search_term}")

            except Exception as e:
                logger.error(f"Error in search behavior middleware: {str(e)}")

    def handle_added_to_cart(self, request):
        """Handle logging when user adds a product to the cart."""
        if request.method == 'POST' and 'cart/add' in request.path:
            try:
                user_id = request.resolver_match.kwargs.get('user_id')
                product_id = request.POST.get('product_id') or request.data.get('product_id')

                if user_id and product_id:
                    user = User.objects.get(user_id=user_id)
                    product = Product.objects.get(product_id=product_id)

                    # Log cart addition activity
                    UserBrowsingBehavior.objects.create(
                        user=user,
                        product=product,
                        activity_type='added_to_cart',
                        interaction_value=1.0,
                        timestamp=now(),
                        content=f"{product.name}"
                    )
                    logger.info(f"User {user.username} added product {product.name} to cart")

            except User.DoesNotExist:
                logger.error(f"User with ID {user_id} does not exist")
            except Product.DoesNotExist:
                logger.error(f"Product with ID {product_id} does not exist")
            except Exception as e:
                logger.error(f"Error in adding to cart logging: {str(e)}")

    def process_response(self, request, response):
        """Set cookies for newly created users."""
        if hasattr(request, 'new_user_id'):
            response.set_cookie('user_id', request.new_user_id, max_age=3600*24*30)  # Cookie valid for 30 days
        return response
