# seller_dashboard/views.py
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from users.decorators import seller_required
from .serializers import AdSerializer, ProductSerializer, ProductAdSerializer
from .models import Ad, ProductAd
from products.models import Product

# Create your views here.
@api_view(['GET'])
def get_ads(request):
    ads = Ad.objects.all()
    serialized_data = AdSerializer(ads, many=True).data
    return Response(serialized_data)

@seller_required
def seller_dashboard(request):
    return JsonResponse({"message": "Welcome to Seller Dashboard"})
