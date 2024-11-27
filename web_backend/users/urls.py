from django.urls import path, include
from .views import login_view, logout_view, register, GoogleSignUpView, GoogleAuthCallback, forgot_password, reset_password, verify_email, update_user, get_user_bank_accounts, create_user_bank_account, update_user_bank_account, delete_user_bank_account
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
from .views import AdminUserRoleUpdateView
#

urlpatterns = [
    path('register/', register, name="register"),
    path('login/', login_view, name="login_view"),
    path('logout/', logout_view, name="logout_view"),
    path('auth/signup/google/', GoogleSignUpView, name='GoogleSignUpView'),
    path('auth/callback/', GoogleAuthCallback, name='GoogleAuthCallback'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password/', reset_password, name='reset_password'),
    path('verify_email/', verify_email, name='verify_email'),
    path('update_user/', update_user, name='update_user'),
    path('bank_accounts/<int:user_id>/', get_user_bank_accounts, name='get_user_bank_accounts'),
    path('bank_account/create/<int:user_id>/', create_user_bank_account, name='create_user_bank_account'),
    path('bank_account/update/<int:bank_account_id>/', update_user_bank_account, name='update_user_bank_account'),
    path('bank_account/delete/<int:bank_account_id>/', delete_user_bank_account, name='delete_user_bank_account'),
    path('admin/update-user-role/<int:user_id>/', AdminUserRoleUpdateView.as_view(), name='admin-update-user-role'),
    
]

urlpatterns = format_suffix_patterns(urlpatterns)
