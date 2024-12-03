from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth import logout
from .serializers import UserSerializer, LoginSerializer, RoleSerializer, UserBankAccountSerializer
# from web_backend.models import Role, User, UserBankAccount
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
import jwt
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from urllib.parse import urlencode
import requests
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .decorators import admin_required
# from .models import User, Role
from web_backend.models import *

# Register User
@csrf_exempt
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Handle password
            password = serializer.validated_data.get('password')
            if password:
                hashed_password = make_password(password)
                serializer.validated_data['password'] = hashed_password
            # Create user
            user = User.objects.create(**serializer.validated_data)
            if not user.role:
                role_instance, created = Role.objects.get_or_create(role_name="User")
                user.role = role_instance
                user.save()
            # Generate verification token
            verification_token = get_random_string(32)
            user.reset_token = verification_token
            user.save()
            # Send email with verification link
            verification_link = f"http://127.0.0.1:8000/api/verify_email/?token={verification_token}"
            send_mail(
                subject="Verify Your Email",
                message=f"Hi {user.username},\n\nPlease verify your email by clicking the link below:\n{verification_link}\n\nThank you!",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response(
                {"message": "User registered successfully. A verification email has been sent."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Verify Email
@csrf_exempt
@api_view(['GET'])
def verify_email(request):
    token = request.GET.get('token')
    if not token:
        return Response({"error": "Verification token is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(reset_token=token)
        user.reset_token = None  # Clear the token after verification
        user.save()
        return redirect('http://127.0.0.1:8000/api/login/')  # Redirect to login page
    except User.DoesNotExist:
        return Response({"error": "Invalid verification token."}, status=status.HTTP_404_NOT_FOUND)

# Login User
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
                    token = jwt.encode({'user_id': user.user_id}, settings.JWT_SECRET_KEY, algorithm='HS256')
                    response = Response({'message': 'Login successful', 'token': token}, status=status.HTTP_200_OK)
                    response.set_cookie(
                        'user_token',  # Cookie name
                        token,  # Token value
                        max_age=36000,  # Expiry time in seconds
                        httponly=True,  # Prevent JavaScript access
                        secure=True,  # Only send over HTTPS
                        samesite='Lax'  # SameSite security policy
                    )
                    return response
                else:
                    return Response({"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Logout User
@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        response = Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie('user_token')  # Remove the cookie when logging out
        return response
    return Response({"error": "User not authenticated"}, status=status.HTTP_400_BAD_REQUEST)


# Google Sign-Up View to generate Google OAuth login URL
@api_view(['POST'])
def GoogleSignUpView(request):
    if request.method == 'POST':
        # Google OAuth login URL
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


# Google OAuth Callback to exchange authorization code for tokens and user info
@api_view(['GET'])
def GoogleAuthCallback(request):
    code = request.GET.get('code')  # Get the authorization code from query parameters
    if not code:
        return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Exchange the code for an access token
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
        return Response({"error": "Failed to get token from Google", "details": token_info},
                        status=status.HTTP_400_BAD_REQUEST)

    access_token = token_info.get('access_token')
    # Fetch user information from Google
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

    # Check if the user already exists
    try:
        user = User.objects.get(email=email)  # Try to find the user by email
        return Response({"message": "Email already exists. Please log in."}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        # Create new user if email doesn't exist
        username = email.split('@')[0] + get_random_string(4)  # Generate a random username
        password = get_random_string(8)  # Generate a random password
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password=make_password(password),  # Hash the password before saving
        )
        role_instance, created = Role.objects.get_or_create(role_name="User")  # Assign a default role
        user.role = role_instance
        user.save()

        # Generate a JWT for the new user
        token = jwt.encode({'user_id': user.user_id}, settings.SECRET_KEY, algorithm='HS256')

        return Response({
            "message": "User signed up successfully via Google.",
            "token": token
        }, status=status.HTTP_201_CREATED)

# Reset Password View
@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')  # User's email
    username = request.data.get('username')  # User's username
    old_password = request.data.get('old_password')  # Old password
    new_password = request.data.get('new_password')  # New password

    if not all([email, username, old_password, new_password]):
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email, username=username)
        if check_password(old_password, user.password):  # Validate old password
            user.password = make_password(new_password)  # Hash and save the new password
            user.save()
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"error": "User not found with the provided email and username."},
                        status=status.HTTP_404_NOT_FOUND)

# Forgot Password View
@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')  # Get email from request data
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
        new_password = get_random_string(8)  # Generate a random password
        user.password = make_password(new_password)  # Hash the password before saving
        user.save()

        # Send the new password via email
        send_mail(
            subject="Your New Password",
            message=f"Hi {user.username}, your new password is: {new_password}",
            from_email="your_email@example.com",  # Change to your actual email
            recipient_list=[email],
            fail_silently=False,
        )
        return Response(
            {"message": "A new password has been sent to your email."},
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response({"error": "User not found with the provided email."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Update User Information View
@api_view(['PUT'])
def update_user(request):
    user_id = request.data.get('user_id')  # Get `user_id` from request data
    if not user_id:
        return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        # Retrieve the user with the provided user_id
        user = User.objects.get(user_id=user_id)

        # Update user fields from request data
        fields_to_update = ['full_name', 'email', 'phone_number', 'address']
        for field in fields_to_update:
            if field in request.data:
                setattr(user, field, request.data[field])

        # Save the updated user information
        user.save()

        # Return the updated user data
        return Response(
            {
                "message": "User information updated successfully.",
                "updated_data": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "address": user.address,
                },
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get User Bank Accounts View
@api_view(['GET'])
def get_user_bank_accounts(request, user_id):
    try:
        # Retrieve bank accounts for the user with the provided user_id
        bank_accounts = UserBankAccount.objects.filter(user__user_id=user_id)
        serializer = UserBankAccountSerializer(bank_accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserBankAccount.DoesNotExist:
        return Response({"error": "No bank accounts found for the user."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create User Bank Account View
@api_view(['POST'])
def create_user_bank_account(request, user_id):
    try:
        # Retrieve user by user_id
        user = User.objects.get(user_id=user_id)

        # Validate and create a bank account for the user
        serializer = UserBankAccountSerializer(data=request.data, context={'user_id': user_id})
        if serializer.is_valid():
            serializer.save()  # Save the bank account information
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Update User Bank Account View
@api_view(['PUT'])
def update_user_bank_account(request, bank_account_id):
    try:
        # Retrieve the bank account by ID
        bank_account = UserBankAccount.objects.get(pk=bank_account_id)
    except UserBankAccount.DoesNotExist:
        return Response({'detail': 'Tài khoản ngân hàng không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

    # Update the bank account information
    serializer = UserBankAccountSerializer(bank_account, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()  # Save changes to the bank account
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete User Bank Account View
@api_view(['DELETE'])
def delete_user_bank_account(request, bank_account_id):
    try:
        # Retrieve the bank account by ID
        bank_account = UserBankAccount.objects.get(pk=bank_account_id)
    except UserBankAccount.DoesNotExist:
        return Response({'detail': 'Tài khoản ngân hàng không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

    # Delete the bank account
    bank_account.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

class AdminUserRoleUpdateView(APIView):
    permission_classes = [IsAdminUser]  # Only admin can access this view

    def put(self, request, user_id):
        try:
            # Retrieve the user by user_id
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get role_id from the request data
        role_id = request.data.get('role_id')
        if not role_id:
            return Response({'error': 'Role ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the role by role_id
        try:
            role = Role.objects.get(role_id=role_id)
        except Role.DoesNotExist:
            return Response({'error': 'Invalid Role ID'}, status=status.HTTP_404_NOT_FOUND)

        # Update the user's role
        user.role = role
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)