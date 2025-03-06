from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from .models import User

class AnonymousUser:
    @property
    def is_authenticated(self):
        return False

class AuthenticatedUser:
    def __init__(self, user):
        self._user = user

    @property
    def is_authenticated(self):
        return True

    def __getattr__(self, name):
        return getattr(self._user, name)

class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            # Lấy token từ header
            token = auth_header.split(' ')[1]
            # Giải mã token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            # Lấy user từ database
            user = User.objects.get(user_id=payload['user_id'])
            # Trả về trực tiếp đối tượng User
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token đã hết hạn')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token không hợp lệ')
        except User.DoesNotExist:
            raise AuthenticationFailed('User không tồn tại')

    def authenticate_header(self, request):
        return 'Bearer'
