from rest_framework import serializers
from .models import Role, UserBankAccount, User

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'role_name']

class UserBankAccountSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.user_id', read_only=True)  # Lấy user_id từ đối tượng User liên kết

    class Meta:
        model = UserBankAccount
        fields = ['account_id', 'account_number', 'bank_name', 'user_id']

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.role_name', read_only=True)  # Lấy tên role từ Role model

    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'role_name']
