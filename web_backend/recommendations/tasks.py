from celery import shared_task
from django.utils.timezone import now
import numpy as np
from .serializers import ProductSerializer
from .ml_models import KnowledgeGraphEmbedding, NeuralCollaborativeFiltering, LSTMRecommender, ExplicitFactorModel
@shared_task(name="celery.ping")
def ping():
    return "pong"

@shared_task
def add(x, y):
    return x + y

@shared_task(bind=True)
def generate_recommendations(self, user_id):
    from web_backend.models import User, Product, Comment, UserBrowsingBehavior, ProductAd  # Moved imports here
    from django.core.cache import cache 
    # Tạo cache key
    cache_key = f"recommendations:{user_id}"
    
    results = {"user_id": user_id}  # Kết quả phải chứa user_id
    # Kiểm tra cache
    cached_result = cache.get(cache_key)
    if cached_result:
        print(f"Dữ liệu đã tồn tại trong cache với key: {cache_key}")
        return cached_result
    results = {}

    # 1. Knowledge Graph Recommendation
    try:
        active_users = User.objects.filter(updated_at__gte="2024-01-01")[:100]        
        popular_products = Product.objects.filter(sales_strategy__gte=10)[:100]        
        triples = [(u.user_id, 0, p.product_id) for u in active_users for p in popular_products]
        kg_model = KnowledgeGraphEmbedding(num_entities=len(User.objects.all()) + len(Product.objects.all()), num_relations=1)
        kg_model.train(triples)
        recommended_indices = kg_model.predict(user_id, 0)
        kg_recommendations = Product.objects.filter(product_id__in=recommended_indices)
        results['knowledge_graph'] = ProductSerializer(kg_recommendations, many=True).data
    except Exception as e:
        results['knowledge_graph'] = str(e)

    # 2. Popular Products
    try:
        popular_products = Product.objects.order_by('-sales_strategy', '-rating')[:10]
        results['popular_products'] = ProductSerializer(popular_products, many=True).data
    except Exception as e:
        results['popular_products'] = str(e)

    # 3. Neural Collaborative Filtering
    try:
        user_behavior = UserBrowsingBehavior.objects.filter(user_id=user_id)
        user_ids = np.array([behavior.user.user_id for behavior in user_behavior])
        product_ids = np.array([behavior.product.product_id for behavior in user_behavior])
        ratings = np.array([1 if behavior.activity_type == 'purchase' else 0 for behavior in user_behavior])
        max_user_id = max(user_ids) if len(user_ids) > 0 else 0
        max_product_id = max(product_ids) if len(product_ids) > 0 else 0
        ncf = NeuralCollaborativeFiltering(num_users=max_user_id + 1, num_products=max_product_id + 1)
        ncf.train(np.column_stack((user_ids, product_ids)), ratings)
        recommended_products = []
        for product_id in Product.objects.values_list('product_id', flat=True):
            if product_id <= max_product_id:
                score = ncf.predict(user_id, product_id)
                recommended_products.append((product_id, score))
        recommended_products = sorted(recommended_products, key=lambda x: x[1], reverse=True)[:10]
        ncf_recommendations = Product.objects.filter(product_id__in=[prod[0] for prod in recommended_products])
        results['ncf'] = ProductSerializer(ncf_recommendations, many=True).data
    except Exception as e:
        results['ncf'] = str(e)

    # 4. LSTM Recommendation
    try:
        behaviors = UserBrowsingBehavior.objects.filter(user_id=user_id).order_by('timestamp')[:10]
        product_ids = [behavior.product.product_id for behavior in behaviors]
        if len(product_ids) < 10:
            raise ValueError("Not enough browsing data to make predictions.")
        X = np.array([product_ids[:-1]])
        y = np.zeros(len(Product.objects.all()))
        y[product_ids[-1]] = 1
        lstm = LSTMRecommender(num_products=len(Product.objects.all()))
        lstm.train(X, np.array([y]))
        recommended_ids = lstm.predict_next_product(product_ids[-10:])
        lstm_recommendations = Product.objects.filter(product_id__in=(recommended_ids))
        results['lstm'] = ProductSerializer(lstm_recommendations, many=True).data
    except Exception as e:
        results['lstm'] = str(e)

    # 5. Sentiment-based Recommendation
    try:
        comments = Comment.objects.filter(user_id=user_id)
        product_embeddings = np.random.rand(len(Product.objects.all()), 50)
        sentiment_model = ExplicitFactorModel(product_embeddings)
        recommended_indices = sentiment_model.recommend(user_id, [c.comment for c in comments])
        sentiment_recommendations = Product.objects.filter(product_id__in=(recommended_indices))
        results['sentiment'] = ProductSerializer(sentiment_recommendations, many=True).data
    except Exception as e:
        results['sentiment'] = str(e)
    # Lọc các trường cần thiết
    filtered_results = []

    # Kết hợp tất cả sản phẩm từ các danh mục khác nhau
    for category, items in results.items():
        for item in items:
            product = Product.objects.get(product_id=item["product_id"])
            # Get the most recent discount percentage
            recent_ad = product.productad_set.order_by('-ad__updated_at', '-ad__created_at').first()
            discount_percentage = recent_ad.ad.discount_percentage if recent_ad else None
            filtered_results.append({
                "product_id": item["product_id"],
                "name": item["name"],
                "price": item["price"],
                "rating": item.get("rating"),
                "sales_strategy": item.get("sales_strategy"),
                "discount": discount_percentage,  # Get the most recent discount percentage
            })
    # Lưu kết quả vào cache
    cache.set(cache_key, filtered_results, timeout=86400)  # Timeout là 1 ngày
    print(f"Kết quả đã được lưu vào cache với key: {cache_key}")
    return filtered_results