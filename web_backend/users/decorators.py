from django.http import JsonResponse
from functools import wraps
# from .models import User
from web_backend.models import *

def admin_required(view_func):
    # Check if user is authenticated and has an 'admin' role
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Ensure the user is authenticated and has a role
        if not request.user.is_authenticated or not hasattr(request.user, 'role') or request.user.role.role_name != 'admin':
            return JsonResponse({'error': 'You do not have permission to access this resource.'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def seller_required(view_func):
    # Check if user is authenticated and has a 'seller' role
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Ensure the user is authenticated and has a role
        if not request.user.is_authenticated or not hasattr(request.user, 'role') or request.user.role.role_name != 'seller':
            return JsonResponse({'error': 'You do not have permission to access this resource.'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
