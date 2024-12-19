# recommendations/urls.py
from django.urls import path
from .views import BatchRecommendationsView, GetBatchRecommendationsView
#, KnowledgeGraphRecommendationView, PopularProductsForNewUsers, PopularProductsView, RecommendationView, LSTMRecommendationView, SentimentBasedRecommendationView, get_task_status, test_task

urlpatterns = [
    # #Đề xuất sản phẩm dựa trên mối quan hệ giữa người dùng và sản phẩm trong Knowledge Graph.
    # path('knowledge/<int:user_id>/', KnowledgeGraphRecommendationView.as_view(), name='knowledge_graph_recommendation'),
    # #Đề xuất các sản phẩm phổ biến nhất, phù hợp cho người dùng mới hoặc người dùng không có lịch sử tương tác.
    # path('popular/', PopularProductsView.as_view(), name='popular_products'),
    # #Đề xuất sản phẩm cá nhân hóa dựa trên Neural Collaborative Filtering (NCF).
    # path('recommendation/<int:user_id>/', RecommendationView.as_view(), name='recommendation'),
    # #Đề xuất sản phẩm tiếp theo mà người dùng có khả năng quan tâm, dựa trên chuỗi hành vi.
    # path('lstm/<int:user_id>/', LSTMRecommendationView.as_view(), name='lstm_recommendation'),
    # #Đề xuất sản phẩm dựa trên phân tích cảm xúc từ đánh giá mà người dùng đã để lại.
    # path('sentiment/<int:user_id>/', SentimentBasedRecommendationView.as_view(), name='sentiment_recommendation'),
    # path('recommendations/popular-products/', PopularProductsForNewUsers.as_view(), name='popular-products-new-users'),
    # path('test-task/', test_task, name='test_task'),
    # path('task-status/<str:task_id>/', get_task_status, name='task_status'),
    path('recommendations/batch/<int:user_id>/', BatchRecommendationsView.as_view(), name='batch_recommendations'),
    path('recommendations/batch-status/<str:task_id>/', GetBatchRecommendationsView.as_view(), name='batch_recommendations_status'),
]
