from django.utils.timezone import now
from web_backend.models import UserBrowsingBehavior, Product
import re

class UserActivityLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = request.user if request.user.is_authenticated else None

        if user:
            # Ghi nhận lịch sử tìm kiếm
            if "search" in request.path and request.method == "GET":
                self.log_activity(user, "search", request.GET.get("q", ""))

            # Ghi nhận lịch sử xem sản phẩm
            elif re.search(r'products/\d+', request.path) and request.method == "GET":
                product_id = self.extract_product_id(request.path)
                if product_id:
                    self.log_activity(user, "view", product_id)

            # Ghi nhận lịch sử mua hàng
            elif "checkout" in request.path and request.method == "POST":
                product_id = request.POST.get("product_id")
                self.log_activity(user, "purchase", product_id)

        return response

    def log_activity(self, user, activity_type, interaction_value):
        UserBrowsingBehavior.objects.create(
            user=user,
            activity_type=activity_type,
            interaction_value=interaction_value,
            timestamp=now()
        )

    def extract_product_id(self, path):
        match = re.search(r'products/(?P<product_id>\d+)', path)
        return match.group('product_id') if match else None
