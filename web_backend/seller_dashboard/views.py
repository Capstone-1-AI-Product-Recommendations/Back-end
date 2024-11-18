# seller_dashboard/views.py
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from datetime import date
from users.decorators import seller_required
from .serializers import AdSerializer, ProductSerializer, ProductAdSerializer
from .models import Ad, ProductAd
from products.models import Product

# Create your views here.

@api_view(['GET'])
@seller_required
def get_ads(request):
    ads = Ad.objects.all()
    serialized_data = AdSerializer(ads, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)

# API tạo quảng cáo
@api_view(['POST'])
@seller_required
def create_ad(request):
    serializer = AdSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Ad created successfully',
            'ad': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API để lấy danh sách tối đa 3 quảng cáo dành cho banner trang homepage. (Chỉ trả về những quảng cáo đang trong thời gian hiệu lực.)
@api_view(['GET'])
def get_homepage_banners(request):
    """
    Mỗi quảng cáo bao gồm thông tin sản phẩm liên quan nếu có.
    """
    try:
        today = date.today()
        # Lọc các quảng cáo đang hoạt động và lấy tối đa 3 quảng cáo mới nhất
        active_ads = Ad.objects.filter(start_date__lte=today, end_date__gte=today).order_by('-start_date')[:3]

        # Serialize dữ liệu quảng cáo
        serialized_ads = []
        for ad in active_ads:
            # Tìm product ads liên quan đến quảng cáo hiện tại
            product_ads = ProductAd.objects.filter(ad=ad)
            serialized_product_ads = ProductAdSerializer(product_ads, many=True).data

            # Kết hợp thông tin quảng cáo và sản phẩm liên quan
            ad_data = AdSerializer(ad).data
            ad_data['related_products'] = serialized_product_ads  # Thêm sản phẩm liên quan
            serialized_ads.append(ad_data)

        return Response(serialized_ads, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)