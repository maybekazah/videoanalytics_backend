
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

from api.models import CameraSettings
from api.serializers.serializers import (
    CameraSettingsSerializer
)
from drf_spectacular.utils import extend_schema

    

# TODO в репозитории вынести обращения к бд
# TODO для авторизированных сделать
class CameraSettingsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Получить все настройки камер",
        description="Возвращает список всех настроек камер.",
        responses={
            200: CameraSettingsSerializer(many=True),
            400: {"описание": "ошибка запроса"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def get(self, request):
        try:
            # Получение всех настроек
            settings = CameraSettings.objects.all()
            serializer = CameraSettingsSerializer(settings, many=True)
            return Response(serializer.data)
        except Exception as e:
            logging.error(f"непредвиденная ошибка при получении данных по настройкам камеры: {str(e)}", exc_info=True)
            return Response({"ошибка сервера": f": {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Создать новые настройки камеры",
        description="Создаёт новые настройки для камеры.",
        request=CameraSettingsSerializer,
        responses={
            201: CameraSettingsSerializer,
            400: {"описание": "ошибка запроса"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def post(self, request):
        try:
            # Создание новых настроек
            serializer = CameraSettingsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"ошибка при создании настроек камеры: {str(e)}", exc_info=True)
            return Response({"ошибка": f": {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CameraSettingsDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return CameraSettings.objects.get(pk=pk)
        except CameraSettings.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Получить настройки камеры по ID",
        description="Возвращает настройки камеры по её ID.",
        responses={
            200: CameraSettingsSerializer,
            400: {"описание": "ошибка запроса"},
            404: {"описание": "настройки камеры не найдены"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def get(self, request, pk):
        try:
            settings = self.get_object(pk)
            serializer = CameraSettingsSerializer(settings)
            return Response(serializer.data)
        except Http404:
            logging.warning(f"Camera settings with id {pk} not found.")
            return Response({"error": "Camera settings not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error(f"Unexpected error while fetching camera settings: {str(e)}", exc_info=True)
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Обновить настройки камеры по ID",
        description="Полностью обновить настройки камеры по её ID.",
        request=CameraSettingsSerializer,
        responses={
            200: CameraSettingsSerializer,
            400: {"описание": "ошибка запроса"},
            404: {"описание": "настройки камеры не найдены"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def put(self, request, pk):
        try:
            settings = self.get_object(pk)
            serializer = CameraSettingsSerializer(settings, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            logging.warning(f"настройки камеры {pk} не найдены")
            return Response({"ошибка": "настройки камеры не найдены"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error(f"ошибка при обновлении настроек камеры: {str(e)}", exc_info=True)
            return Response({"ошибка": f": {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Частично обновить настройки камеры по ID",
        description="Частичное обновление настроек камеры по её ID.",
        request=CameraSettingsSerializer,
        responses={
            200: CameraSettingsSerializer,
            400: {"описание": "ошибка запроса"},
            404: {"описание": "настройки камеры не найдены"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def patch(self, request, pk):
        try:
            settings = self.get_object(pk)
            serializer = CameraSettingsSerializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            logging.warning(f"настройки камеры для {pk} не найдены")
            return Response({"ошибка": "настройки камеры не найдены"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error(f"ошибка при обновлении настроек камеры: {str(e)}", exc_info=True)
            return Response({"ошибка": f": {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

