from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from web_backend.models import *
from products.serializers import ProductSerializer
import joblib
from django.shortcuts import render
from django.http import JsonResponse
import numpy as np
import pandas as pd
from django.db.models import Avg, Count, Sum

# Tải các mô hình đã huấn luyện
svd = joblib.load('recommendations/models/svd_model.pkl')
cosine_sim = joblib.load('recommendations/models/cosine_sim.pkl')
user_similarity = joblib.load('recommendations/models/user_similarity.pkl')
user_item_matrix = joblib.load('recommendations/models/user_item_matrix.pkl')

from sklearn.preprocessing import MinMaxScaler

# Loại bỏ sự tương đồng chính nó
np.fill_diagonal(cosine_sim, 0)

# Chuẩn hóa ma trận cosine similarity
scaler = MinMaxScaler()
cosine_sim_normalized = scaler.fit_transform(cosine_sim)
# Hàm Hybrid Recommendation
def hybrid_recommendation(user_item_matrix, cosine_sim_normalized, svd, user_similarity, product_id, user_id, top_n=10):
    user_idx = user_id - 1
    cf_scores = svd.inverse_transform(svd.transform(user_item_matrix))[user_idx]
    
    try:
        product = Product.objects.get(product_id=product_id)
        product_idx = product.product_id - 1
    except Product.DoesNotExist:
        return []
    
    # Sử dụng ma trận cosine similarity đã chuẩn hóa
    cbf_scores = cosine_sim_normalized[product_idx]
    user_idx_similarity = np.argsort(user_similarity[user_idx])[::-1]
    user_similarity_scores = user_similarity[user_idx, user_idx_similarity]
    
    # Kết hợp CF, CBF và User-User Similarity
    hybrid_scores = 0.2 * cf_scores + 0.5 * cbf_scores + 0.3 * user_similarity_scores[:len(cf_scores)]
    recommended_idx = np.argsort(hybrid_scores)[-top_n:][::-1]
    
    recommended_products = []
    for idx in recommended_idx:
        product = Product.objects.filter(product_id=idx + 1).first()
        if product:
            recommended_products.append(product.product_id)
    
    return recommended_products

# Hàm đề xuất cho người dùng mới (Cold Start Problem)
def recommend_for_new_user(product_id, top_n=5):
    # 1. Đề xuất sản phẩm phổ biến (Top sản phẩm có lượng bán cao)
    popular_products = Product.objects.annotate(
        sales_count=Sum('orderitem__quantity')
    ).order_by('-sales_count')[:top_n]  # Lấy top N sản phẩm phổ biến
    
    # Nếu không có sản phẩm phổ biến, trả về danh sách trống
    if not popular_products:
        return []

    # 2. Tính sự tương đồng giữa sản phẩm được đưa vào và các sản phẩm khác (Content-based Filtering)
    try:
        product = Product.objects.get(product_id=product_id)
        product_idx = product.product_id - 1  # Chuyển từ ID (1-based) sang index (0-based)
    except Product.DoesNotExist:
        return []  # Nếu sản phẩm không tồn tại, trả về danh sách trống

    cbf_scores = cosine_sim[product_idx]
    similar_products_idx = np.argsort(cbf_scores)[-top_n:][::-1]  # Sắp xếp sản phẩm tương tự theo điểm cosine giảm dần

    # Lấy tất cả các sản phẩm tương tự từ CBF bằng cách lọc nhiều product_id cùng lúc
    recommended_products = Product.objects.filter(product_id__in=[idx + 1 for idx in similar_products_idx])

    # Kết hợp sản phẩm phổ biến với sản phẩm tương tự từ CBF
    recommended_product_ids = [product.product_id for product in popular_products] + [product.product_id for product in recommended_products]
    
    # Giới hạn số lượng sản phẩm đề xuất tối đa là top_n
    return recommended_product_ids[:top_n]

@api_view(['GET'])
# @permission_classes([AllowAny])
def get_recommended_products(request):
    try:
        product_id = request.GET.get('product_id', '').strip()
        user_id = request.GET.get('user_id', '').strip()

        # Xử lý khi không có product_id
        if not product_id:
            if not user_id or user_id == '0':
                popular_products = Product.objects.annotate(
                    sales_count=Sum('orderitem__quantity', default=0)
                ).order_by('-sales_count')[:10].prefetch_related('productimage_set')

                serialized_data = [
                    {
                        "product_id": product.product_id,
                        "name": product.name,
                        "description": product.description,
                        "price": product.price,
                        "images": [image.file for image in product.productimage_set.all()] if product.productimage_set.exists() else []
                    }
                    for product in popular_products
                ]
                return Response(serialized_data)

            else:
                return Response({"error": "product_id is required for existing users"}, status=400)

        if not product_id.isdigit():
            return Response({"error": "Invalid product_id"}, status=400)

        product_id = int(product_id)

        # Xử lý người dùng mới hoặc người dùng hiện tại
        if not user_id or user_id == '0':
            recommended_product_ids = recommend_for_new_user(product_id)
        else:
            if not user_id.isdigit():
                return Response({"error": "Invalid user_id"}, status=400)

            user_id = int(user_id)
            recommended_product_ids = hybrid_recommendation(
                user_item_matrix,
                cosine_sim,
                svd,
                user_similarity,
                product_id,
                user_id
            )

        recommended_products = Product.objects.filter(product_id__in=recommended_product_ids).prefetch_related(
            'productimage_set')

        serialized_data = [
            {
                "product_id": product.product_id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "images": [image.file for image in product.productimage_set.all()] if product.productimage_set.exists() else []
            }
            for product in recommended_products
        ]

        return Response(serialized_data)

    except ValueError:
        return Response({"error": "Invalid parameter values"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
