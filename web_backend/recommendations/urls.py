# recommendations/urls.py
from django.urls import path

from .views import BatchRecommendationsView, GetBatchRecommendationsView, trigger_recommend_behavior
#, KnowledgeGraphRecommendationView, PopularProductsForNewUsers, PopularProductsView, RecommendationView, LSTMRecommendationView, SentimentBasedRecommendationView, get_task_status, test_task

urlpatterns = [
    path('recommendations/batch/<int:user_id>/', BatchRecommendationsView.as_view(), name='batch_recommendations'),
    path('recommendations/batch-status/<str:task_id>/', GetBatchRecommendationsView.as_view(), name='batch_recommendations_status'),
    path('recommend_behavior/', trigger_recommend_behavior, name='recommend_behavior'),
]