from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .models import ProductRecommendation
from web_backend.models import *
from products.serializers import ProductSerializer


@api_view(['GET'])
def get_recommended_products(request):
    if request.user.is_authenticated:
        # Get the recommendations for the authenticated user, and prefetch the product for efficiency
        recommendations = ProductRecommendation.objects.filter(user=request.user).select_related('product').order_by(
            '-recommended_at')

        # Serialize the product data from the recommendations
        recommended_products = [rec.product for rec in recommendations]
    else:
        recommended_products = []  # If not authenticated, return an empty list

    # Serialize the list of recommended products
    serialized_data = ProductSerializer(recommended_products, many=True).data
    return Response(serialized_data)
