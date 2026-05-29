from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        read_only_fields = ['id']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                data['user'] = user
            else:
                raise serializers.ValidationError('Invalid username or password.')
        else:
            raise serializers.ValidationError('Must include username and password.')
        
        return data


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'operator'),
            password=validated_data['password']
        )
        return user
