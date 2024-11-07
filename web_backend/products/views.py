from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from web_backend.models import Product, ProductAd, ProductRecommendation
# Create your views here.


@api_view(['GET'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    recommendations = ProductRecommendation.objects.filter(product=product)
    unique_recommendations = {rec.user.username: rec for rec in recommendations}.values()
    recommendation_data = [{
        "user": recommendation.user.username
    } for recommendation in unique_recommendations]
    ads = ProductAd.objects.filter(product=product)
    unique_ads = {ad.product_ad_id: ad for ad in ads}.values()
    ad_data = [{
        "ad_title": ad.ad.title if ad.ad else "No Title"
    } for ad in unique_ads]
    product_data = {
        "name": product.name,
        "price": product.price,
        "category": product.category.category_name if product.category else None,
        "description": product.description,
        "seller": product.seller.username if product.seller else None,
        "quantity": product.quantity,
        "recommendations": recommendation_data,
        "ads": ad_data
    }

    return Response(product_data, status=status.HTTP_200_OK)
    