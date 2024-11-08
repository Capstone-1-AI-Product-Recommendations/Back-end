from django.urls import path, include
from .views import login_view, logout_view, register, GoogleSignUpView
from rest_framework.urlpatterns import format_suffix_patterns

#

urlpatterns = [
    path('register/', register, name="register"),
    path('login/', login_view, name="login_view"),
    path('logout/', logout_view, name="logout_view"),
    path('auth/signup/google/', GoogleSignUpView, name='google_signup'),
]

urlpatterns = format_suffix_patterns(urlpatterns)