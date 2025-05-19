from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    is_admin = serializers.BooleanField()


class LoginResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = UserSerializer()
    

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()


class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField()