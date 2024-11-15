# admin_dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_users, name='get-users'),
    path('users/create/', views.create_user, name='create-user'),
    path('users/<int:user_id>/', views.get_user_detail, name='get-user-detail'),
    path('users/<int:user_id>/update/', views.update_user, name='update-user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete-user'),
]
