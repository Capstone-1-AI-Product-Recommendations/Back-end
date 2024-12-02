from rest_framework import serializers
# from .models import Role, UserBankAccount, User
from web_backend.models import *

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'role_name']

class UserBankAccountSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.user_id', read_only=True)  # Get the user_id from the related User model

    class Meta:
        model = UserBankAccount
        fields = ['account_id', 'account_number', 'bank_name', 'user_id']

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.role_name', read_only=True)  # Get the role_name from the related Role model
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)  # Added city field
    province = serializers.CharField(max_length=100, required=False, allow_blank=True)  # Added province field

    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'role_name', 'city', 'province']  # Added city and province fields