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
joblib.dump('svd', 'recommendations/models/svd_model.pkl')
joblib.dump('tfidf', 'recommendations/models/tfidf_model.pkl')
joblib.dump('cosine_sim', 'recommendations/models/cosine_sim.pkl')
joblib.dump('user_similarity', 'recommendations/models/user_similarity.pkl')
joblib.dump('user_item_matrix', 'recommendations/models/user_item_matrix.pkl')

# Hàm Hybrid Recommendation
def hybrid_recommendation(user_item_matrix, cosine_sim, svd, user_similarity, product_id, user_id, top_n=10):
    user_idx = user_id - 1
    cf_scores = svd.inverse_transform(svd.transform(user_item_matrix))[user_idx]

    try:
        product = Product.objects.get(product_id=product_id)
        product_idx = product.product_id - 1
    except Product.DoesNotExist:
        return []

    cbf_scores = cosine_sim[product_idx]
    user_idx_similarity = np.argsort(user_similarity[user_idx])[::-1]
    user_similarity_scores = user_similarity[user_idx, user_idx_similarity]

    hybrid_scores = cf_scores + cbf_scores + user_similarity_scores[:len(cf_scores)]
    recommended_idx = np.argsort(hybrid_scores)[-top_n:][::-1]

    recommended_products = []
    for idx in recommended_idx:
        product = Product.objects.filter(product_id=idx + 1).first()
        if product:
            recommended_products.append(product.product_id)

    return recommended_products

# Hàm đề xuất cho người dùng mới (Cold Start Problem)
def recommend_for_new_user(product_id, top_n=5):
    # 1. Đề xuất sản phẩm phổ biến (Sản phẩm có số lượt mua cao)
    popular_products = Product.objects.order_by('-sales_count')[:top_n]  # Lấy sản phẩm phổ biến từ cơ sở dữ liệu

    # 2. Tính sự tương đồng giữa sản phẩm mới với các sản phẩm khác (Content-based Filtering)
    # Lấy chỉ mục của sản phẩm phẩm trong cơ sở dữ liệu
    try:
        product_idx = Product.objects.get(product_id=product_id).id
    except Product.DoesNotExist:
        return []  # Trả về danh sách rỗng nếu s���n phẩm không tồn tại

    cbf_scores = cosine_sim[product_idx]

    # 3. Kết hợp sản phẩm phổ biến với các sản phẩm có sự tương đồng cao từ CBF
    # Sử dụng chỉ mục để truy vấn các sản phẩm có sự tương đồng cao
    similar_products_idx = np.argsort(cbf_scores)[-top_n:][::-1]  # Sắp xếp các sản phẩm theo sự tương đồng giảm dần

    # Lấy ID các sản phẩm tương tự từ danh sách đã sắp xếp
    recommended_products = []
    for idx in similar_products_idx:
        product = Product.objects.filter(id=idx).first()
        if product:
            recommended_products.append(product.product_id)

    return recommended_products

@api_view(['GET'])
@permission_classes([AllowAny])
def get_recommended_products(request):
    try:
        # Lấy tham số
        product_id = request.GET.get('product_id', '').strip()
        user_id = request.GET.get('user_id', '').strip()

        # Xử lý khi không có product_id
        if not product_id:
            if not user_id or user_id == '0':
                # Đề xuất sản phẩm phổ biến cho người dùng mới
                popular_products = Product.objects.annotate(
                    sales_count=Sum('orderitem__quantity')
                ).order_by('-sales_count')[:10]

                serialized_data = ProductSerializer(popular_products, many=True).data
                return Response(serialized_data)

            else:
                return Response({"error": "product_id is required for existing users"}, status=400)

        product_id = int(product_id)

        # Xử lý người dùng mới hoặc người dùng hiện tại
        if not user_id or user_id == '0':
            recommended_product_ids = recommend_for_new_user(product_id)
        else:
            user_id = int(user_id)
            recommended_product_ids = hybrid_recommendation(
                user_item_matrix,
                cosine_sim,
                svd,
                user_similarity,
                product_id,
                user_id
            )

        recommended_products = Product.objects.filter(product_id__in=recommended_product_ids)
        serialized_data = ProductSerializer(recommended_products, many=True).data

        return Response(serialized_data)

    except ValueError:
        return Response({"error": "Invalid parameter values"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
