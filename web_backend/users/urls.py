from django.urls import path, include
from .views import login_view, logout_view, register, GoogleSignUpView, GoogleAuthCallback, forgot_password, reset_password
from rest_framework.urlpatterns import format_suffix_patterns

#

urlpatterns = [
    path('register/', register, name="register"),
    path('login/', login_view, name="login_view"),
    path('logout/', logout_view, name="logout_view"),
    path('auth/signup/google/', GoogleSignUpView, name='GoogleSignUpView'),
    path('auth/callback/', GoogleAuthCallback, name='GoogleAuthCallback'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password/', reset_password, name='reset_password'),
]

urlpatterns = format_suffix_patterns(urlpatterns)