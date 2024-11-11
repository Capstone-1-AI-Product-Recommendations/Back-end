# users/urls.py
from django.urls import path
from .views import AdminUserRoleUpdateView

urlpatterns = [
    path('admin/update-user-role/<int:user_id>/', AdminUserRoleUpdateView.as_view(), name='admin-update-user-role'),
]
