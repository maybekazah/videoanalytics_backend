from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.configs.logger import setup_logging
setup_logging()
import logging

from rest_framework import status

from api.serializers.auth import (
    LoginSerializer,
    LoginResponseSerializer,
    ErrorSerializer,
    LogoutResponseSerializer
)

from drf_spectacular.utils import extend_schema

import os


HTTPONLY_ACCESS_TOKEN = os.getenv('HTTPONLY_ACCESS_TOKEN', "True").lower() == "true"
SECURE_ACCESS_TOKEN = os.getenv('SECURE_ACCESS_TOKEN', "True").lower() == "true"
MAX_AGE_ACCESS_TOKEN = int(os.getenv('MAX_AGE_ACCESS_TOKEN'))


HTTPONLY_REFRESH_TOKEN = os.getenv('HTTPONLY_REFRESH_TOKEN', "True").lower() == "true"
SECURE_REFRESH_TOKEN = os.getenv('SECURE_REFRESH_TOKEN', "True").lower() == "true"
MAX_AGE_REFRESH_TOKEN = int(os.getenv('MAX_AGE_REFRESH_TOKEN'))



# auth <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class AuthenticatedTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"ошибка": "refresh token не найден"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Проверяем валидность refresh токена
            token = RefreshToken(refresh_token)
            
            # Создаем новый access токен
            new_access_token = str(token.access_token)
            
            response = Response({"message": "Токен успешно обновлен"}, status=status.HTTP_200_OK)
            response.set_cookie(
                'access_token',
                new_access_token,
                httponly=HTTPONLY_ACCESS_TOKEN,
                secure=SECURE_ACCESS_TOKEN,
                max_age=60*MAX_AGE_ACCESS_TOKEN,
                samesite='Lax'
            )
            return response
            
        except Exception as e:
            return Response(
                {"ошибка": f"Ошибка обновления токена: {str(e)}"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        

class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer 

    @extend_schema(
        summary="Авторизация пользователя",
        description="Выполняет авторизацию пользователя с использованием логина и пароля",
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,  
            400: ErrorSerializer,          
            401: ErrorSerializer,          
            500: ErrorSerializer           
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                try:
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)

                    # устанавливаем токены в куки с флагами HttpOnly, Secure, SameSite
                    response = Response({
                        "message": "Login successful",
                        "user": {
                            "username": user.username,
                            "is_admin": user.is_superuser
                        }
                    })
                    response.set_cookie(
                        'access_token', access_token,
                        httponly=False,
                        secure=SECURE_ACCESS_TOKEN,
                        max_age=60*MAX_AGE_ACCESS_TOKEN, 
                        samesite='Lax'
                    )

                    response.set_cookie(
                        'refresh_token', refresh_token,
                        httponly=False,
                        secure=SECURE_REFRESH_TOKEN,
                        max_age=60*MAX_AGE_REFRESH_TOKEN,
                        samesite='Lax'
                    )

                    return response 
                except Exception as e:
                    return Response({"ошибка": f"токен не сгенерирован: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"ошибка": "неавторизован"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutResponseSerializer
    @extend_schema(
        summary="Выход из системы",
        description="Аннулирует refresh токен и завершает сессию пользователя",
        responses={
            200: serializer_class,  
            400: ErrorSerializer,
            401: ErrorSerializer,
            403: ErrorSerializer,
            500: ErrorSerializer 
        }
    )
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({"ошибка": "refresh token"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                token = RefreshToken(refresh_token)
                if token['user_id'] != request.user.id:
                    return Response({"ошибка": "другой пользователь"}, status=status.HTTP_403_FORBIDDEN)
                token.blacklist()
            except Exception as e:
                return Response({"ошибка": f"refresh token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)
    
            response = Response({"сообщение": "вы вышли из системы"}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token', httponly=True, secure=True, samesite='Lax') 
            response.delete_cookie('refresh_token', httponly=True, secure=True, samesite='Lax')
            return response
        except Exception as e:
            return Response({"ошибка": f"непредвиденная ошибка: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



# для проверки авторизации для выдачи картинок
class AuthCheckAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Проверка авторизации",
        description="Возвращает 200 OK, если пользователь авторизован, иначе 401",
        responses={
            200: {"description": "Пользователь авторизован"},
            401: {"description": "Неавторизован"}
        }
    )
    def get(self, request):
        return Response({"message": "Пользователь авторизован"}, status=status.HTTP_200_OK)