from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from web_backend.models import Product
from .serializer import ProductSerializer, CRUDProductSerializer
# from django.db.models import Prefetch

@api_view(['GET'])
def product_detail(request, product_id):
    try:
        product = Product.objects.select_related('category', 'seller') \
                                  .prefetch_related('productrecommendation_set', 'productad_set__ad', 'comment_set') \
                                  .get(product_id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['POST'])
def create_product(request):
    serializer = CRUDProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CRUDProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        updated_product = serializer.save()
        return Response(ProductSerializer(updated_product).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response({"detail": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)