from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, get_user_model
from .serializer import UserSerializer, LoginSerializer, RoleSerializer
from web_backend.models import Role, User
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
import jwt, requests
from django.utils.http import urlencode
from django.conf import settings


@api_view(['POST'])
def register(request):
    if request.method == 'POST':    
        serializer = UserSerializer(data=request.data) # Khởi tạo serializer với dữ liệu yêu cầu        
        if serializer.is_valid():
            password = serializer.validated_data.get('password')  # Lấy mật khẩu từ dữ liệu đã xác thực
            if password:
                hashed_password = make_password(password)
                serializer.validated_data['password'] = hashed_password # Cập nhật mật khẩu đã mã hóa vào dữ liệu
            user = User.objects.create(**serializer.validated_data)
            if not user.role:
                role_instance, created = Role.objects.get_or_create(role_name="User") # Tạo vai trò 'User' nếu chưa tồn tại
                user.role = role_instance # Gán vai trò cho người dùng
                user.save() 
            return Response({"message": "User registered successfully", "user": serializer.data}, status=status.HTTP_201_CREATED)       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

@api_view(['POST'])
def login_view(request):    
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            try:
                user = User.objects.get(username=username) # Tìm người dùng với tên đăng nhập tương ứng
                if check_password(password, user.password):
                    token = jwt.encode({'user_id': user.user_id}, 'your_secret_key', algorithm='HS256') # Tạo token JWT
                    response = Response({'message': 'Login successful',}, status=status.HTTP_200_OK)
                    response.set_cookie( # Thiết lập cookie để lưu token trên trình duyệt
                        'user_token',  # Tên cookie
                        'token',  # Giá trị cookie (token, ID người dùng, v.v.)
                        max_age=36000,  # Thời gian tồn tại cookie (ví dụ: 1 giờ)
                        httponly=True,  # Không cho phép JavaScript truy cập cookie
                        secure=True,  # Chỉ gửi cookie qua kết nối HTTPS
                        samesite='Lax'  # Quy định về bảo mật cookie
                    )
                    return response
                else:
                    return Response({"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        response = Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie('user_token')  # Xóa cookie chứa token khi logout
        return response
    return Response({"error": "User not authenticated"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def GoogleSignUpView(request):
    if request.method == 'POST':
        # Tạo liên kết đăng nhập Google.
        google_login_url = "https://accounts.google.com/o/oauth2/v2/auth"
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        client_id = settings.GOOGLE_CLIENT_ID
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
        }
        google_login_link = f"{google_login_url}?{urlencode(params)}"
        return Response({
            "message": "Click the link to sign up or log in with Google.",
            "google_login_link": google_login_link
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
def GoogleAuthCallback(request):
    code = request.GET.get('code')  # Lấy mã ủy quyền từ các tham số truy vấn   
    if not code:
        return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)
    # Đổi mã ủy quyền để lấy mã thông hành truy cập
    google_token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(google_token_url, data=data)
    token_info = response.json()
    if response.status_code != 200:
        return Response({"error": "Failed to get token from Google", "details": token_info}, status=status.HTTP_400_BAD_REQUEST)
    access_token = token_info.get('access_token')
    # Sử dụng mã thông hành truy cập để lấy thông tin người dùng từ Google
    google_user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(google_user_info_url, headers=headers)
    user_info = user_info_response.json()

    if user_info_response.status_code != 200:
        return Response({"error": "Failed to fetch user info from Google"}, status=status.HTTP_400_BAD_REQUEST)
    email = user_info.get('email')
    full_name = user_info.get('name')
    if not email:
        return Response({"error": "No email returned from Google"}, status=status.HTTP_400_BAD_REQUEST)
    # Kiểm tra xem người dùng đã tồn tại dựa trên email hay chưa
    try:
        user = User.objects.get(email=email)  # Cố gắng tìm người dùng qua email
        return Response({"message": "Email already exists. Please log in."}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        # Tạo người dùng mới nếu email chưa tồn tại
        username = email.split('@')[0] + get_random_string(4)  # Dùng phần đầu của email và thêm chuỗi ngẫu nhiên
        password = get_random_string(8)  # random password
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password=password,  
        )
        role_instance, created = Role.objects.get_or_create(role_name="User")
        user.role = role_instance
        user.save()
        # Step 5: Tạo mã JWT cho người dùng mới
        token = jwt.encode({'user_id': user.user_id}, 'your_secret_key', algorithm='HS256')
        return Response({
            "message": "User signed up successfully via Google."
        }, status=status.HTTP_201_CREATED)