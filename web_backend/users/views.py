from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth import logout
from .serializers import LoginUserSerializer, RegisUserSerializer, LoginSerializer, RoleSerializer, UserBankAccountSerializer, UserBrowsingBehaviorSerializer, UserSerializer, NotificationSerializer
from web_backend.models import Role, User, UserBankAccount, UserBrowsingBehavior
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
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
from web_backend.models import *
import jwt
from django.core.validators import validate_email
from django.shortcuts import render
import re, random
from django.forms import ValidationError 
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAdminUser
# from .decorators import admin_required
# from .models import User, Role
# from .serializers import UserSerializer

def validate_email_format(value):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, value):
        raise ValidationError("Invalid email format.") 

@csrf_exempt
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = RegisUserSerializer(data=request.data)  # Khởi tạo serializer với dữ liệu yêu cầu        

        if serializer.is_valid():
            # Kiểm tra email
            email = serializer.validated_data.get('email')
            try:
                validate_email(email)  # Kiểm tra định dạng email
            except ValidationError:
                return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

            # Kiểm tra xem email đã tồn tại chưa
            if User.objects.filter(email=email).exists():
                return Response({"error": "Email already in use."}, status=status.HTTP_400_BAD_REQUEST)
            # Xử lý mật khẩu
            password = serializer.validated_data.get('password')
            if password:
                hashed_password = make_password(password)
                serializer.validated_data['password'] = hashed_password
            # Create user
            user = User.objects.create(**serializer.validated_data)
            if not user.role:
                role_instance, created = Role.objects.get_or_create(role_name="user")
                user.role = role_instance
                user.save()
            # Generate verification token
            verification_token = get_random_string(32)
            user.reset_token = verification_token
            user.save()
            # Send email with verification link
            verification_link = f"http://127.0.0.1:8000/api/verify_email/?token={verification_token}"
            try:
                send_mail(
                    subject="Verify Your Email",
                    message=f"Hi {user.username},\n\nPlease verify your email by clicking the link below:\n{verification_link}\n\nThank you!",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                user.delete()  # Xóa người dùng nếu gửi email thất bại
                return Response({"error": f"Failed to send verification email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
                    user_serializer = LoginUserSerializer(user) 
                    response = Response({'message': 'Login successful', 'user': user_serializer.data, 'token': token }, status=status.HTTP_200_OK)                   
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
def logout_view(request, user_id):
    response = Response({"message": f"User logged out successfully"}, status=status.HTTP_200_OK)
    response.delete_cookie('user_token')  # Xóa cookie nếu tồn tại
    return response

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

        # Tạo mã JWT cho người dùng mới
        token = jwt.encode({'user_id': user.user_id}, 'your_secret_key', algorithm='HS256')


        # Generate a JWT for the new user
        # token = jwt.encode({'user_id': user.user_id}, settings.SECRET_KEY, algorithm='HS256')

        return Response({"message": "User signed up successfully via Google."}, status=status.HTTP_201_CREATED)

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
    email = request.data.get('email')  # Lấy email từ yêu cầu    
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)    
    # Kiểm tra định dạng email
    try:
        validate_email_format(email)
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
    # Lấy đúng email (chuyển thành chữ thường để tránh sai lệch)
    email = email.lower().strip()    
    try:
        user = User.objects.get(email=email)        
        # Tạo mã xác thực gồm 6 chữ số
        verification_code = random.randint(100000, 999999)        
        # Lưu mã xác thực vào cơ sở dữ liệu
        # VerificationCode.objects.create(email=email, code=verification_code) 
        request.session['verification_code'] = verification_code  
        request.session.modified = True  # Đảm bảo session được lưu lại ngay   
        # Gửi mã xác thực qua email
        send_mail(
            subject="Your Password Reset Verification Code",
            message=f"Hi {user.username}, your verification code is: {verification_code}",
            from_email="your_email@example.com",
            recipient_list=[email],
            fail_silently=False,
        )        
        return Response({"detail": "Verification code sent to your email.", "redirect_url": "http://127.0.0.1:8000/api/verify_reset_code/",}, status=status.HTTP_200_OK)    
    except User.DoesNotExist:
        return Response({"error": "User not found with the provided email."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def verify_reset_code(request):
    email = request.data.get('email')
    verification_code = request.session.get('verification_code')
    
    if not email or not verification_code:
        return Response({"error": "Email and verification code are required."}, status=status.HTTP_400_BAD_REQUEST)
    # Kiểm tra mã xác thực từ session
    session_code = request.session.get('verification_code')    
    if not session_code:
        return Response({"error": "Verification code has expired or is invalid."}, status=status.HTTP_400_BAD_REQUEST)

    if session_code != verification_code:
        return Response({"error": "Invalid verification code. Please check the code or request a new one."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Lấy người dùng từ email
        user = User.objects.get(email=email.lower().strip())
        return Response({"detail": "Verification successful, you can now reset your password.", "redirect_url": "http://127.0.0.1:8000/api/new_password/"}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"error": "User not found with the provided email."}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def new_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not email or not new_password or not confirm_password:
        return Response({"error": "Email, new password, and confirm password are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Kiểm tra mật khẩu mới và mật khẩu xác nhận có khớp không
    if new_password != confirm_password:
        return Response({"error": "The new password and confirm password do not match."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Lấy người dùng từ email
        user = User.objects.get(email=email.lower().strip())

        # Đặt lại mật khẩu mới
        user.password = make_password(new_password)
        user.save()

        # Xóa mã xác thực khỏi session sau khi đặt lại mật khẩu
        if 'verification_code' in request.session:
            del request.session['verification_code']
        return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"error": "User not found with the provided email."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['PUT'])
def update_user_info(request, user_id):
    try:
        # Retrieve the user with the provided user_id
        user = User.objects.get(user_id=user_id)

        # Update user fields from request data
        fields_to_update = ['full_name', 'email', 'phone_number', 'address', 'city']
        for field in fields_to_update:
            if field in request.data:
                if field == 'email':  # Kiểm tra email
                    email = request.data[field]
                    try:
                        validate_email(email)  # Kiểm tra định dạng email
                    except ValidationError:
                        return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)
                    # Kiểm tra xem email đã được sử dụng chưa
                    if User.objects.filter(email=email).exclude(user_id=user_id).exists():
                        return Response({"error": "Email already in use."}, status=status.HTTP_400_BAD_REQUEST)
                setattr(user, field, request.data[field])

        # Save the updated user information
        user.save()

        # Return the updated user data
        user_info = {
            'full_name': user.full_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'address': user.address,
            'city': user.city,
        }
        return Response(
            {
                "message": "User information updated successfully.",
                "updated_data": user_info,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
def user_bank_accounts_list_create(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        accounts = UserBankAccount.objects.filter(user=user)
        serializer = UserBankAccountSerializer(accounts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserBankAccountSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Chi tiết, cập nhật hoặc xóa tài khoản ngân hàng
@api_view(['GET', 'PUT', 'DELETE'])
def user_bank_account_detail(request, user_id, bank_account_id):
    try:
        user = User.objects.get(pk=user_id)
        account = UserBankAccount.objects.get(pk=bank_account_id, user=user)
    except (User.DoesNotExist, UserBankAccount.DoesNotExist):
        return Response({"error": "User or Bank Account not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserBankAccountSerializer(account)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserBankAccountSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        account.delete()
        return Response({"message": "Bank account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_user_behavior(request, user_id):
    behaviors = UserBrowsingBehavior.objects.filter(user_id=user_id).order_by('-timestamp')
    if behaviors.exists():
        serializer = UserBrowsingBehaviorSerializer(behaviors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"detail": "No browsing behavior found for this user."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_user_notifications(request, user_id):
    try:
        # Get top 10 notifications for the user
        notifications = Notification.objects.filter(user_id=user_id).order_by('-created_at')[:10]
        
        # Serialize notifications
        serialized_data = NotificationSerializer(notifications, many=True).data
        
        return Response(serialized_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_notification_status(request, user_id):
    try:
        # Get notification_id from request data
        notification_id = request.data.get('notification_id')

        if notification_id is None:
            return Response({"error": "notification_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the notification
        notification = Notification.objects.get(notification_id=notification_id, user_id=user_id)
        
        # Update is_read status to 0
        notification.is_read = 0
        notification.save()
        
        return Response({"message": "Notification status updated successfully"}, status=status.HTTP_200_OK)
    
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_user_info(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        user_info = {
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'address': user.address,
            'city': user.city,
        }
        return JsonResponse(user_info, status=200)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

from web_backend.models import Order, OrderItem, Product, Shop, ProductImage

@api_view(['GET'])
def get_user_orders(request, user_id):
    try:
        orders = Order.objects.filter(user_id=user_id)
        if not orders.exists():
            return Response({"detail": "No orders found for this user."}, status=status.HTTP_404_NOT_FOUND)

        order_data = []
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                product = item.product
                shop = product.shop
                product_image = product.images.first().file if product.images.exists() else None
                order_data.append({
                    "order_id": order.order_id,
                    "product_id": product.product_id,
                    "product_name": product.name,
                    "quantity": item.quantity,
                    "status": order.status,
                    "shop_name": shop.shop_name if shop else None,
                    "image": product_image,
                })

        return Response(order_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
