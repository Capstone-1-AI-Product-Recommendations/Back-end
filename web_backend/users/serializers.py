from rest_framework import serializers
from .models import User, Role

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'full_name', 'role_name', 'created_at', 'updated_at']
