
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status

from api.configs.logger import setup_logging
setup_logging()
import logging

from rest_framework import status
from django.http import Http404

from api.models import Camera
from api.serializers.serializers import (
    CameraSerializer
)
from drf_spectacular.utils import extend_schema


# TODO в репозитории вынести обращения к бд
# TODO для авторизированных сделать
class CameraView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Получить все камеры",
        description="Возвращает список всех камер.",
        responses={
            200: CameraSerializer(many=True),
            400: {"описание": "неверные данные"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def get(self, request):
        try:
            # Получение списка всех камер
            cameras = Camera.objects.all()
            serializer = CameraSerializer(cameras, many=True)
            return Response(serializer.data)
        except Exception as e:
            logging.error(f"непредвиденная ошибка: {str(e)}", exc_info=True)
            return Response({"ошибка": f": {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Создать новую камеру",
        description="Создаёт новую камеру.",
        request=CameraSerializer,
        responses={
            201: CameraSerializer,
            400: {"описание": "неверные данные"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def post(self, request):
        try:
            # Создание новой камеры
            serializer = CameraSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Unexpected error while creating camera: {str(e)}", exc_info=True)
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CameraDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Camera.objects.get(pk=pk)
        except Camera.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить камеру по ID",
        description="Возвращает камеру по ID.",
        responses={
            200: CameraSerializer,
            400: {"описание": "неверные данные"},
            404: {"описание": "камера не найдена"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def get(self, request, pk):
        try:
            camera = self.get_object(pk)
            serializer = CameraSerializer(camera)
            return Response(serializer.data)
        except Http404:
            logging.warning(f"камера с id {pk} не найдена")
            return Response({"ошибка": "камера не найдена"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error(f"непредвиденная ошибка: {str(e)}", exc_info=True)
            return Response({"ошибка": f"непредвиденная ошибка: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Обновить камеру по ID",
        description="Полностью обновить данные камеры по ID.",
        request=CameraSerializer,
        responses={
            200: CameraSerializer,
            400: {"описание": "неверные данные"},
            404: {"описание": "камера не найдена"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def put(self, request, pk):
        try:
            camera = self.get_object(pk)
            serializer = CameraSerializer(camera, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            logging.warning(f"камера с id {pk} не найдена")
            return Response({"ошибка": "камера не найдена"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error(f"непредвиденная ошибка при обновлении данных: {str(e)}", exc_info=True)
            return Response({f"непредвиденная ошибка: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Частичное обновление камеры по ID",
        description="Частичное обновление данных камеры по ID.",
        request=CameraSerializer,
        responses={
            200: CameraSerializer,
            400: {"описание": "неверные данные"},
            404: {"описание": "камера не найдена"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def patch(self, request, pk):
        try:
            camera = self.get_object(pk)
            serializer = CameraSerializer(camera, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            logging.warning(f"камера с id {pk} не найдена")
            return Response({"ошибка": "камера не найдена"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error(f"непредвиденная ошибка при частичном обновлении данных: {str(e)}", exc_info=True)
            return Response({f"непредвиденная ошибка: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

