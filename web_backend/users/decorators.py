# decorators.py trong app `users`
from django.http import JsonResponse
from functools import wraps
from .models import User

def admin_required(view_func):
    # Kiểm tra xem người dùng đã đăng nhập hay chưa và có vai trò là "admin" hay không
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role.role_name != 'admin':
            return JsonResponse({'error': 'You do not have permission to access this resource.'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def seller_required(view_func):
    # Kiểm tra xem người dùng đã đăng nhập hay chưa và có vai trò là "seller" hay không
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role.role_name != 'seller':
            return JsonResponse({'error': 'You do not have permission to access this resource.'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
