
from django.urls import path
# from .views import AdminUserRoleUpdateView
from django.urls import path, include
from .views import *
from rest_framework.urlpatterns import format_suffix_patterns
# from .views import AdminUserRoleUpdateView
#

urlpatterns = [
    path('register/', register, name="register"),
    path('login/', login_view, name="login_view"),
    path('logout/<int:user_id>/', logout_view, name="logout_view"),
    path('auth/signup/google/', GoogleSignUpView, name='GoogleSignUpView'),
    path('auth/callback/', GoogleAuthCallback, name='GoogleAuthCallback'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('verify_reset_code/', verify_reset_code, name='verify_reset_code'),
    path('new_password/', new_password, name='new_password'),
    path('reset_password/', reset_password, name='reset_password'),
    path('verify_email/', verify_email, name='verify_email'),
    path('update_user/<int:user_id>/', update_user, name='update_user'),
    
    # path('admin/update-user-role/<int:user_id>/', AdminUserRoleUpdateView.as_view(), name='admin-update-user-role'),
    path('update_user/<int:user_id>/', update_user, name='update_user'),
    path('bank_accounts/user/<int:user_id>/', user_bank_accounts_list_create, name='user_bank_accounts_list_create'),
    path('bank_accounts/user/<int:user_id>/account/<int:bank_account_id>/', user_bank_account_detail, name='user_bank_account_detail'),
    path('user/behavior/<int:user_id>/', get_user_behavior, name='get_user_behavior'), 
    path('register_seller/<int:user_id>/', register_seller, name='register_seller'),   
    path('accept_seller/<int:admin_id>/', accept_or_reject_seller, name='accept_seller'),  
]

# Apply format suffix patterns (if required for API formats like JSON, XML, etc.)
urlpatterns = format_suffix_patterns(urlpatterns)
