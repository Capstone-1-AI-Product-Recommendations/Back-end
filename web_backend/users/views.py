from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, get_user_model
from .serializer import UserSerializer, LoginSerializer, RoleSerializer
from web_backend.models import Role, User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User as DjangoUser
from django.utils.crypto import get_random_string

@api_view(['POST'])
def register(request):
    if request.method == 'POST':    
        serializer = UserSerializer(data=request.data)        
        if serializer.is_valid():
            password = serializer.validated_data.get('password')
            if password:
                hashed_password = make_password(password)
                serializer.validated_data['password'] = hashed_password
            user = User.objects.create(**serializer.validated_data)
            if not user.role:
                role_instance, created = Role.objects.get_or_create(role_name="User")
                user.role = role_instance
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
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    return Response({'message': 'Login successful',}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

            except User.DoesNotExist:
                return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
    return Response({"error": "User not authenticated"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def GoogleSignUpView(request):
    user_data = request.data
    email = user_data.get('email')
    user = User.objects.filter(email=email).first()    
    if user:
        return Response({"message": "User already exists."}, status=200)
    username = user_data.get('username', f"user_{get_random_string(length=8)}")
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