from urllib import response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, get_user_model
from .serializer import UserSerializer, LoginSerializer, RoleSerializer
from web_backend.models import Role, User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User as DjangoUser
from django.utils.crypto import get_random_string
import jwt

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
    user_data = request.data
    email = user_data.get('email')
    user = User.objects.filter(email=email).first() # Kiểm tra nếu người dùng đã tồn tại với email đó    
    if user:
        return Response({"message": "User already exists."}, status=200)
    username = user_data.get('username', f"user_{get_random_string(length=8)}") # Lấy tên người dùng hoặc tạo tên ngẫu nhiên
    while User.objects.filter(username=username).exists():  # Kiểm tra trùng tên người dùng
        username = f"user_{get_random_string(length=8)}"
    password = get_random_string(length=12) 
    user = User.objects.create(
        username=username,
        email=email,
        password=password,
    )
    role_name = user_data.get('role', 'User')
    role, created = Role.objects.get_or_create(role_name=role_name)
    user.role = role
    user.save()
    return Response({"message": "User registered successfully!", "username": user.username}, status=status.HTTP_201_CREATED)