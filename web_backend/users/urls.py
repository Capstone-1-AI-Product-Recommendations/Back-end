from django.urls import path, include
from .views import new_password, verify_reset_code, login_view, logout_view, register, GoogleSignUpView, GoogleAuthCallback, forgot_password, reset_password, verify_email, update_user, user_bank_accounts_list_create, user_bank_account_detail, get_user_behavior
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
# from .views import AdminUserRoleUpdateView
#

urlpatterns = [
    path('register/', register, name="register"),
    path('login/', login_view, name="login_view"),
    path('logout/', logout_view, name="logout_view"),
    path('auth/signup/google/', GoogleSignUpView, name='GoogleSignUpView'),
    path('auth/callback/', GoogleAuthCallback, name='GoogleAuthCallback'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('verify_reset_code/', verify_reset_code, name='verify_reset_code'),
    path('new_password/', new_password, name='new_password'),
    path('reset_password/', reset_password, name='reset_password'),
    path('verify_email/', verify_email, name='verify_email'),
    path('update_user/<int:user_id>/', update_user, name='update_user'),
    path('bank_accounts/user/<int:user_id>/', user_bank_accounts_list_create, name='user_bank_accounts_list_create'),
    path('bank_accounts/user/<int:user_id>/account/<int:bank_account_id>/', user_bank_account_detail, name='user_bank_account_detail'),
    # path('admin/update-user-role/<int:user_id>/', AdminUserRoleUpdateView.as_view(), name='admin-update-user-role'),
    path('user/behavior/<int:user_id>/', get_user_behavior, name='get_user_behavior'),    
]

urlpatterns = format_suffix_patterns(urlpatterns)
