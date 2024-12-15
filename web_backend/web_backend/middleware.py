import logging
from django.utils.timezone import now
from web_backend.models import UserBrowsingBehavior, Product, User, CartItem, Cart

# Cấu hình logging
logger = logging.getLogger(__name__)

class UserActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method == 'GET' and 'products/detail' in request.path:
            # Lấy user_id và product_id từ URL
            if request.resolver_match is not None:
                user_id = request.resolver_match.kwargs.get('user_id')
            else:
                # Xử lý trường hợp không tìm thấy resolver_match
                logger.error("No resolver match found for the request.")
                return response  # Hoặc xử lý theo cách khác
            print("user_id",user_id)
            product_id = request.resolver_match.kwargs.get('product_id')

            if user_id and product_id:
                try:
                    user = User.objects.get(user_id=user_id)
                    product = Product.objects.get(product_id=product_id)

                    # Lưu hành động vào database
                    UserBrowsingBehavior.objects.create(
                        user=user,
                        product=product,
                        activity_type='viewed_product',
                        interaction_value=1.0,
                        timestamp=now(),
                    )

                    logger.info(f"User {user.username} viewed product {product.name}")

                except User.DoesNotExist:
                    logger.error(f"User with ID {user_id} does not exist")
                except Product.DoesNotExist:
                    logger.error(f"Product with ID {product_id} does not exist")
            # Lưu hành động tìm kiếm sản phẩm
        if request.method == 'GET' and 'search/' in request.path:
            user_id = request.GET.get('user_id')  # Nếu user_id được truyền qua query params, hoặc có thể lấy từ session

            if user_id:
                search_term = request.GET.get('search_term')
                category = request.GET.get('category')
                min_price = request.GET.get('min_price')
                max_price = request.GET.get('max_price')

                # Ghi lại hành động tìm kiếm
                if search_term or category or min_price or max_price:
                    try:
                        user = User.objects.get(id=user_id)

                        # Lưu hành động tìm kiếm vào database
                        UserBrowsingBehavior.objects.create(
                            user=user,
                            activity_type='searched_product',
                            interaction_value=1.0,
                            timestamp=now(),
                        )
                        logger.info(f"User {user.username} searched for products with terms: {search_term}, category: {category}")

                    except User.DoesNotExist:
                        logger.error(f"User with ID {user_id} does not exist")

        # Lưu hành động thêm vào giỏ hàng
        if request.method == 'POST' and 'cart/add' in request.path:
            user_id = request.resolver_match.kwargs.get('user_id')
            product_id = request.POST.get('product_id') or request.data.get('product_id')  # Xử lý cả request từ form và JSON
            
            if user_id and product_id:
                try:
                    user = User.objects.get(user_id=user_id)
                    product = Product.objects.get(product_id=product_id)

                    UserBrowsingBehavior.objects.create(
                        user=user,
                        product=product,
                        activity_type='added_to_cart',
                        interaction_value=1.0,
                        timestamp=now(),
                    )
                    logger.info(f"User {user.username} added product {product.name} to cart")
                except User.DoesNotExist:
                    logger.error(f"User with ID {user_id} does not exist")
                except Product.DoesNotExist:
                    logger.error(f"Product with ID {product_id} does not exist")

        return response