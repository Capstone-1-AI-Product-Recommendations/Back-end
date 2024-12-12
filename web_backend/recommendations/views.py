from rest_framework.decorators import api_view
from rest_framework.response import Response
from web_backend.models import *
from products.serializers import ProductSerializer
import joblib
from django.shortcuts import render
from django.http import JsonResponse
import numpy as np
import pandas as pd

# Tải các mô hình đã huấn luyện
svd = joblib.load('recommendations/models/svd_model.pkl')
tfidf = joblib.load('recommendations/models/tfidf_model.pkl')
cosine_sim = joblib.load('recommendations/models/cosine_sim.pkl')
user_similarity = joblib.load('recommendations/models/user_similarity.pkl')
user_item_matrix = joblib.load('recommendations/models/user_item_matrix.pkl')

# Hàm Hybrid Recommendation
def hybrid_recommendation(user_item_matrix, cosine_sim, svd, user_similarity, product_id, top_n=10):
    user_idx = 0  # Assuming we are recommending for the first user
    cf_scores = svd.inverse_transform(svd.transform(user_item_matrix))[user_idx]

    # Truy vấn sản phẩm từ cơ sở dữ liệu Django (thay vì dùng pandas)
    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        return []  # Trả về danh sách rỗng nếu sản phẩm không tồn tại

    product_idx = product.id  # Lấy chỉ mục của sản phẩm trong cơ sở dữ liệu
    cbf_scores = cosine_sim[product_idx]

    user_idx_similarity = np.argsort(user_similarity[user_idx])[::-1]  # Sắp xếp người dùng tương tự theo độ tương đồng
    user_similarity_scores = user_similarity[user_idx, user_idx_similarity]

    hybrid_scores = cf_scores + cbf_scores + user_similarity_scores[:len(cf_scores)]  # Cộng 3 loại điểm số
    recommended_idx = np.argsort(hybrid_scores)[-top_n:][::-1]

    recommended_products = []
    for idx in recommended_idx:
        product = Product.objects.filter(id=idx).first()
        if product:
            recommended_products.append(product.product_id)

    return recommended_products

# Hàm đề xuất cho người dùng mới (Cold Start Problem)
def recommend_for_new_user(product_id, top_n=5):
    # 1. Đề xuất sản phẩm phổ biến (Sản phẩm có số lượt mua cao)
    popular_products = Product.objects.order_by('-sales_count')[:top_n]  # Lấy sản phẩm phổ biến từ cơ sở dữ liệu

    # 2. Tính sự tương đồng giữa sản phẩm mới với các sản phẩm khác (Content-based Filtering)
    # Lấy chỉ mục của sản phẩm trong cơ sở dữ liệu
    try:
        product_idx = Product.objects.get(product_id=product_id).id
    except Product.DoesNotExist:
        return []  # Trả về danh sách rỗng nếu sản phẩm không tồn tại

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
def get_recommendations(request):
    try:
        # Kiểm tra nếu người dùng đã đăng ký hoặc cung cấp user_id
        user_id = request.GET.get('user_id')  # Không ép kiểu int ngay, kiểm tra sự tồn tại
        product_id = int(request.GET.get('product_id', 101))  # Mặc định là sản phẩm 101 nếu không có product_id

        # Nếu không có user_id, xử lý như người dùng mới (cold start)
        if not user_id:
            # Người dùng mới, gọi hàm recommend_for_new_user
            recommended_products = recommend_for_new_user(product_id)
        else:
            # Người dùng có lịch sử hành vi, gọi hybrid_recommendation
            user_id = int(user_id)  # Chuyển thành int nếu có user_id
            recommended_products = hybrid_recommendation(user_item_matrix, cosine_sim, svd, user_similarity, product_id)

        # Trả về kết quả dưới dạng JSON
        response_data = {
            'user_id': user_id if user_id else 'new_user',  # Ghi rõ 'new_user' nếu không có user_id
            'product_id': product_id,
            'recommended_products': recommended_products
        }

        return JsonResponse(response_data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['GET'])
def get_recommended_products(request):
    try:
        if request.user.is_authenticated:        
            product_id = int(request.GET.get('product_id', 101))  # Mặc định là 101 nếu không có product_id
            user_id = int(request.GET.get('user_id', 1))  # Mặc định là người dùng 1 nếu không có user_id

            # Lấy danh sách sản phẩm đề xuất
            recommendations = hybrid_recommendation(user_item_matrix, cosine_sim, svd, user_similarity, product_id)
            # Get the recommendations for the authenticated user, and prefetch the product for efficiency
            # recommendations = ProductRecommendation.objects.filter(user=request.user).select_related('product').order_by(
            #     '-recommended_at')

            # Serialize the product data from the recommendations
            recommended_products = [rec.product for rec in recommendations]
        else:
            recommended_products = []  # If not authenticated, return an empty list

        # Serialize the list of recommended products
        serialized_data = ProductSerializer(recommended_products, many=True).data
        return Response(serialized_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)