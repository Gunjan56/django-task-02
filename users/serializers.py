from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        role = validated_data.get('role')
        if role and role.lower() != 'employee':
            raise serializers.ValidationError("Role must be 'employee'.")
        user = CustomUser.objects.create_user(**validated_data)
        return user

class ManagerSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if validated_data['role'].lower() != 'manager':
            raise serializers.ValidationError('Role should be "manager".')  
        user = CustomUser.objects.create_user(**validated_data)
        return user
      