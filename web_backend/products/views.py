from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from web_backend.models import Product, ProductAd, ProductRecommendation
from .serializer import CRUDProductSerializer


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

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def product_crud(request, pk=None):
    if request.method == 'GET' and pk:
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CRUDProductSerializer(product)
        return Response(serializer.data)

    if request.method == 'POST':
        product_data = request.data
        if Product.objects.filter(name=product_data.get('name')).exists():
            return Response({"error": "Product already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CRUDProductSerializer(data=product_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT' and pk:
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CRUDProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and pk:
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    