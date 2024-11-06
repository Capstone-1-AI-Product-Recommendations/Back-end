# views.py của app products
from django.shortcuts import render
from .models import Product
from .serializers import ProductSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def product_list(request):
    try:
        # Lấy tất cả sản phẩm
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
