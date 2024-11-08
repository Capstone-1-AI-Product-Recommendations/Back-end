from rest_framework import serializers
from web_backend.models import Role, User

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'role_name']
class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(required=False, allow_null=True)
    class Meta:
        model = User
        fields = ['user_id', 'username', 'password', 'email', 'full_name', 'role', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
