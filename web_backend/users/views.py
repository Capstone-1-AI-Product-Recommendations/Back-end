from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, get_user_model
from .serializer import UserSerializer, LoginSerializer 

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully", "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
    return Response({"error": "User not authenticated"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def GoogleLoginView(request):
    user_data = request.data
    user = get_user_model().objects.filter(email=user_data['email']).first()
    if user:
        return Response({"message": "Login successful", "user": user.username}, status=200)
    return Response({"message": "User does not exist"}, status=400)

@api_view(['POST'])
def GoogleRegisterView(request):
    user_data = request.data
    user = get_user_model().objects.filter(email=user_data['email']).first()
    if user:
        return Response({"message": "User already exists."}, status=200)
    user = get_user_model().objects.create_user(
        username=user_data['username'],
        email=user_data['email'],     
        password='randompassword123',  
    )
    return Response({"message": "User registered successfully!"}, status=201)