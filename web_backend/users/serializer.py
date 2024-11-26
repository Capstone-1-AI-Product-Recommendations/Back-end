from rest_framework import serializers
from web_backend.models import Role, User, UserBankAccount, UserBrowsingBehavior

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'role_name']

class UserBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBankAccount
        fields = ['bank_account_id', 'bank_name', 'account_number', 'account_holder_name', 'account_type', 'user']
        read_only_fields = ['user']  # Chỉ có khóa chính là read-only

    # Đảm bảo các trường này là bắt buộc và có giá trị mặc định khi không có dữ liệu
    bank_name = serializers.CharField(required=True)
    account_number = serializers.CharField(required=True)
    account_holder_name = serializers.CharField(required=True)
    account_type = serializers.ChoiceField(choices=[('Savings', 'Savings'), ('Current', 'Current')], required=True)

    def create(self, validated_data):
        # Lấy user_id từ context
        user_id = self.context['user_id']
        user = User.objects.get(user_id=user_id)
        return UserBankAccount.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(required=False, allow_null=True)
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
