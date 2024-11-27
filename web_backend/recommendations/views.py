# views.py của app recommendations
from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
# Create your views here.

@api_view(['GET'])
def get_recommended_products(request):
    if request.user.is_authenticated:
        recommendations = ProductRecommendation.objects.filter(user=request.user).order_by('-recommended_at')
        recommended_products = [rec.product for rec in recommendations]
    else:
        recommended_products = []
    serialized_data = ProductSerializer(recommended_products, many=True).data
    return Response(serialized_data)