from django.urls import path, include
from .views import login_view, logout_view, register, GoogleLoginView, GoogleRegisterView
from rest_framework.urlpatterns import format_suffix_patterns

#

urlpatterns = [
    path('register/', register, name="register"),
    path('login/', login_view, name="login_view"),
    path('logout/', logout_view, name="logout_view"),
    path('auth/login/google/', GoogleLoginView, name='google_login'),
    path('auth/registration/google/', GoogleRegisterView, name='google_register'),
]

urlpatterns = format_suffix_patterns(urlpatterns)