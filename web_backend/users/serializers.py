from rest_framework import serializers
from web_backend.models import Role, User, UserBankAccount, UserBrowsingBehavior
# from .models import User, Role
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'role_name']

class UserBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBankAccount
        fields = ['bank_account_id', 'bank_name', 'account_number', 'account_holder_name', 'account_type', 'user']
        read_only_fields = ['user']
    def create(self, validated_data):
        # Gán user từ context (truyền từ view)
        user = self.context['user']
        validated_data['user'] = user
        return super().create(validated_data)
class RegisUserSerializer(serializers.ModelSerializer):
    # role = RoleSerializer(required=False, allow_null=True)
    bank_accounts = UserBankAccountSerializer(many=True, read_only=True, source='userbankaccount_set')
    class Meta:
        model = User
        fields = ['user_id', 'username', 'password', 'email', 'full_name','address', 'phone_number', 'role', 'bank_accounts', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UserBrowsingBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBrowsingBehavior
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'role_name', 'created_at', 'updated_at']

# class UserBankAccountSerializer(serializers.ModelSerializer):
#     user_id = serializers.IntegerField(source='user.user_id', read_only=True)  # Get the user_id from the related User model

#     class Meta:
#         model = UserBankAccount
#         fields = ['account_id', 'account_number', 'bank_name', 'user_id']

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.role_name', read_only=True)  # Get the role_name from the related Role model
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)  # Added city field
    province = serializers.CharField(max_length=100, required=False, allow_blank=True)  # Added province field

    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'role_name', 'city', 'province']  # Added city and province fields


