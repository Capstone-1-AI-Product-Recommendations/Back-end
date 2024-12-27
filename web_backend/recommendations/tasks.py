from celery import shared_task
from django.utils.timezone import now
import numpy as np
from web_backend.models import UserBehavior
from .serializers import ProductRecommendationSerializer, ProductSerializer
from .ml_models import KnowledgeGraphEmbedding, NeuralCollaborativeFiltering, LSTMRecommender, ExplicitFactorModel
from celery import Celery
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.core.cache import cache
from web_backend.models import User, Product, Comment, UserBehavior
app = Celery('recommendations')

@shared_task(name="celery.ping")
def ping():
    return "pong"

@shared_task
def add(x, y):
    return x + y

@shared_task(bind=True)
def generate_recommendations(self, user_id):
    # Tạo cache key
    cache_key = f"recommendations:{user_id}"
    results = {"user_id": user_id}

    # Kiểm tra cache
    cached_result = cache.get(cache_key)
    if cached_result:
        print(f"Dữ liệu đã tồn tại trong cache với key: {cache_key}")
        return cached_result

    # 1. Knowledge Graph Recommendation
    try:
        active_users = User.objects.filter(created_at__gte="2024-01-01")[:100]
        popular_products = Product.objects.filter(sales_strategy__gte=10)[:100]
        search_queries = UserBehavior.objects.filter(action_type='search').values_list('search_query', flat=True)

        triples = [
            (u.user_id, 0, p.product_id) for u in active_users for p in popular_products
        ]
        for query in search_queries:
            matching_products = Product.objects.filter(name__icontains=query)[:10]
            if matching_products.exists():
                triples += [
                    (u.user_id, 1, p.product_id) for u in active_users for p in matching_products
                ]
        print(f"Triples Sample: {triples[:10]}")

        if not triples:
            print("No triples generated for Knowledge Graph.")
            results['knowledge_graph'] = []
            return

        # kg_model = KnowledgeGraphEmbedding(num_entities=len(User.objects.all()) + len(Product.objects.all()), num_relations=2)
        # kg_model.train(triples)
        
        # recommended_indices = kg_model.predict(user_id, 0)  # Gán giá trị ở đây
        # products = Product.objects.filter(product_id__in=recommended_indices)
        # results['knowledge_graph'] = ProductSerializer(products, many=True).data if products.exists() else []
        # print("Knowledge Graph Recommendations:", results['knowledge_graph'])
        
        if not triples:
            print("No triples generated for Knowledge Graph.")
            results['knowledge_graph'] = []
            return results

        kg_model = KnowledgeGraphEmbedding(num_entities=len(User.objects.all()) + len(Product.objects.all()), num_relations=2)
        kg_model.train(triples)
        
        try:
            recommended_indices = kg_model.predict(user_id, 0)
        except Exception as e:
            print(f"Knowledge Graph Prediction Error: {e}")
            recommended_indices = []
        print(f"Sample Triples: {triples[:10]}")
        print(f"Total Triples Count: {len(triples)}")

        products = Product.objects.filter(product_id__in=recommended_indices)
        results['knowledge_graph'] = ProductSerializer(products, many=True).data if products.exists() else []
        print("Knowledge Graph Recommendations:", results['knowledge_graph'])
                
    except Exception as e:
        results['knowledge_graph'] = []
        print(f"Knowledge Graph Error: {e}")

    # 2. Neural Collaborative Filtering
    try:
        if not user_ids or not product_ids or len(user_ids) != len(product_ids):
            print(f"Data inconsistency: user_ids={len(user_ids)}, product_ids={len(product_ids)}")
            results['ncf'] = []
            return

        user_ids = np.array(user_ids)
        product_ids = np.array(product_ids)
        weights = np.array(weights)

        if user_ids.ndim != 1 or product_ids.ndim != 1:
            print(f"Invalid dimensions: user_ids={user_ids.shape}, product_ids={product_ids.shape}")
            results['ncf'] = []
            return

        ncf = NeuralCollaborativeFiltering(num_users=max_user_id + 1, num_products=max_product_id + 1)
        ncf.train(np.column_stack((user_ids, product_ids)), weights, epochs=5)

        recommended_products = []
        for product_id in Product.objects.values_list('product_id', flat=True):
            if product_id <= max_product_id:
                score = ncf.predict(user_id, product_id)
                recommended_products.append((product_id, score))

        recommended_products = sorted(recommended_products, key=lambda x: x[1], reverse=True)[:10]
        ncf_recommendations = Product.objects.filter(product_id__in=[prod[0] for prod in recommended_products])

        results['ncf'] = ProductSerializer(ncf_recommendations, many=True).data if ncf_recommendations.exists() else []
        print("NCF Recommendations:", results['ncf'])
    except Exception as e:
        results['ncf'] = []
        print(f"NCF Error: {e}")

    # 3. LSTM Recommendation
    try:
        behaviors = UserBehavior.objects.filter(user_id=user_id).order_by('created_at')
        product_ids = [behavior.product_id for behavior in behaviors if behavior.action_type in ['view', 'add_to_cart']]

        # Kiểm tra độ dài chuỗi sản phẩm
        if len(product_ids) < 10:
            print("Not enough browsing data for LSTM recommendation. Using fallback.")
            fallback_products = Product.objects.order_by('-sales_strategy', '-rating')[:10]
            results['lstm'] = ProductSerializer(fallback_products, many=True).data
            return

        # Chuẩn bị dữ liệu cho LSTM
        X = np.array([product_ids[:-1]])  # Chuỗi đầu vào
        y = np.zeros(len(Product.objects.all()))
        y[product_ids[-1]] = 1  # Nhãn cho sản phẩm tiếp theo

        # Huấn luyện mô hình LSTM
        lstm = LSTMRecommender(num_products=len(Product.objects.all()))
        lstm.train(X, np.array([y]))

        # Dự đoán sản phẩm
        recommended_ids = lstm.predict_next_product(product_ids[-10:])
        lstm_recommendations = Product.objects.filter(product_id__in=recommended_ids)

        # Fallback nếu không có sản phẩm nào được dự đoán
        if not lstm_recommendations.exists():
            print("LSTM did not return valid recommendations. Using fallback.")
            fallback_products = Product.objects.order_by('-sales_strategy', '-rating')[:10]
            lstm_recommendations = fallback_products

        # Serialize kết quả
        results['lstm'] = ProductSerializer(lstm_recommendations, many=True).data
        print("LSTM Recommendations:", results['lstm'])
    except Exception as e:
        results['lstm'] = []
        print(f"LSTM Error: {e}")

    # 4. Sentiment-based Recommendation
    try:
    # Lấy dữ liệu bình luận và truy vấn tìm kiếm
        comments = Comment.objects.filter(user_id=user_id)
        search_queries = UserBehavior.objects.filter(user_id=user_id, action_type='search').values_list('search_query', flat=True)
        product_embeddings = np.random.rand(len(Product.objects.all()), 50)

        print(f"Comments: {comments.count()}, Search Queries: {len(search_queries)}")

        # Kết hợp văn bản
        all_texts = [c.comment for c in comments] + list(search_queries)
        print(f"Texts for Sentiment Analysis: {all_texts}")

        # Phân tích sentiment và dự đoán sản phẩm
        sentiment_model = ExplicitFactorModel(product_embeddings)
        recommended_indices = sentiment_model.recommend(user_id, all_texts)
        print(f"Recommended Indices: {recommended_indices}")

        # Chuyển đổi kiểu dữ liệu nếu cần
        valid_indices = [int(idx) for idx in recommended_indices]
        print(f"Valid Recommended Indices: {valid_indices}")

        # Lọc sản phẩm từ bảng Product
        valid_products = Product.objects.filter(product_id__in=valid_indices)
        print(f"Valid Products Count: {valid_products.count()}")

        # Fallback nếu không có sản phẩm
        if not valid_products.exists():
            print("No valid products found. Using fallback recommendations.")
            fallback_products = Product.objects.order_by('-sales_strategy', '-rating')[:10]
            valid_products = fallback_products

        # Serialize kết quả
        results['sentiment'] = ProductSerializer(valid_products, many=True).data
        print(f"Final Sentiment Recommendations: {results['sentiment']}")
    except Exception as e:
        results['sentiment'] = []
        print(f"Sentiment Error: {e}")

    # Tích hợp các kết quả
    try:
        final_scores = {}
        for category, items in results.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                product_id = item.get("product_id")
                if product_id:
                    final_scores[product_id] = final_scores.get(product_id, 0) + item.get("score", 1.0)

        top_products = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        filtered_results = [
            {
                "product_id": p[0],
                # "score": p[1],
                "name": Product.objects.get(product_id=p[0]).name,
                "price": Product.objects.get(product_id=p[0]).price,
                "rating": Product.objects.get(product_id=p[0]).rating
            }
            for p in top_products
        ]
    except Exception as e:
        filtered_results = {"error": str(e)}

    # Lưu cache
    cache.set(cache_key, filtered_results, timeout=86400)  # Lưu cache trong 1 ngày
    print(f"Kết quả đã được lưu vào cache với key: {cache_key}")
    return filtered_results

@shared_task(bind=True)
def recommend_behavior(self, session_id=None, user_id=None):
    from web_backend.models import UserBehavior, Product
    from django.core.cache import cache
    from django.db.models import Q
    from .serializers import ProductSerializer

    try:        
        if not session_id and not user_id:
            return {"error": "Missing session_id or user_id"}

        # Tạo cache key
        cache_key = f"recommend_behavior:{session_id or user_id}"

        # Kiểm tra cache
        cached_result = cache.get(cache_key)
        if cached_result:
            print(f"Kết quả đã tồn tại trong cache với key: {cache_key}")
            return cached_result

        # Lấy dữ liệu hành vi từ UserBehavior
        behaviors = UserBehavior.objects.filter(
            Q(session_id=session_id) | Q(user_id=user_id)
        ).order_by('-created_at')

        if not behaviors.exists():
            return {"error": "No behaviors found for the given session_id or user_id"}

        # Lọc hành vi add_to_cart
        add_to_cart_ids = list(behaviors.filter(
            action_type='add_to_cart'
        ).values_list('product_id', flat=True)[:5])

        # Lọc hành vi view
        view_ids = list(behaviors.filter(
            action_type='view'
        ).values_list('product_id', flat=True)[:5])

        # Kết hợp và loại bỏ các ID trùng lặp
        product_ids = list(set(add_to_cart_ids + view_ids))

        # Lọc hành vi search
        search_queries = list(behaviors.filter(
            action_type='search'
        ).values_list('search_query', flat=True)[:5])

        # Lấy sản phẩm dựa vào product_id
        products_by_id = Product.objects.filter(product_id__in=product_ids)

        # Lấy sản phẩm dựa vào search_query
        products_by_search = Product.objects.none()
        for query in search_queries:
            product_ids_from_query = list(Product.objects.filter(
                name__icontains=query
            ).values_list('product_id', flat=True)[:5])
            products_by_search |= Product.objects.filter(product_id__in=product_ids_from_query)

        # Kết hợp sản phẩm từ hành vi khác nhau
        recommended_products = list(products_by_id) + list(products_by_search)
        
        # Serialize dữ liệu
        serialized_data = ProductSerializer(recommended_products, many=True).data

        cache.set(cache_key, serialized_data, timeout=86400)  # Timeout: 1 ngày
        print(f"Kết quả đã lưu vào cache với key: {cache_key}")

        return serialized_data        
    except Exception as e:
        self.retry(exc=e, countdown=10, max_retries=3)  # Retry nếu có lỗi
        return {"error": str(e)}

#tính năng chatbot
class SearchAndRecommendation:
    def __init__(self, products):
        self.products = products
        self.vectorizer = TfidfVectorizer()
        self.product_vectors = self.vectorizer.fit_transform([
            f"{p.name} {p.description or ''} {p.detail_product or ''}" 
            for p in products
        ])

    def search(self, query, filters=None):
        # Vector hóa truy vấn
        query_vector = self.vectorizer.transform([query])
        # Tính độ tương đồng
        similarity_scores = cosine_similarity(query_vector, self.product_vectors).flatten()
        # Lấy các sản phẩm phù hợp
        top_indices = np.argsort(similarity_scores)[-20:]
        candidates = [self.products[i] for i in top_indices]

        # Áp dụng bộ lọc
        if filters:
            filtered_results = []
            for product in candidates:
                match = True
                if 'price_range' in filters:
                    min_price, max_price = filters['price_range']
                    if not (min_price <= product.price <= max_price):
                        match = False
                if 'subcategory' in filters and product.subcategory_id != filters['subcategory']:
                    match = False
                if 'rating' in filters and product.rating < filters['rating']:
                    match = False
                if match:
                    filtered_results.append(product)
            return filtered_results[:10]
        return candidates[:10]