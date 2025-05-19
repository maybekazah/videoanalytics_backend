from api.configs.logger import setup_logging
setup_logging()
import logging

from drf_spectacular.utils import extend_schema

from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status

from django.http import Http404

from api.serializers.serializers import AlertDataSerializer
from api.services.auth_for_frame_processor import CustomTokenAuthentication
from api.services.postgres_db import create_alert_safely

from api.models import AlertData, Camera


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception as e:
            logging.warning(f"Ошибка аутентификации по cookie: {e}")
            return None


class GetRequiresJWTPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return bool(request.user and request.user.is_authenticated)
        elif request.method == "POST":
            return True
        return False


class AlertDataView(APIView, LimitOffsetPagination):
    serializer_class = AlertDataSerializer
    permission_classes = [GetRequiresJWTPermission]


    def get_authenticators(self):
        if self.request.method == "GET":
            return [CookieJWTAuthentication()]
        elif self.request.method == "POST":
            return [CustomTokenAuthentication()]
        return []


    @extend_schema(
        summary="Получить последние тревоги (с пагинацией)",
        description="Требует JWT-аутентификацию через куки. Возвращает последние alert'ы, отсортированные по дате создания.",
        responses={
            200: AlertDataSerializer(many=True),
            401: {"description": "Требуется JWT-аутентификация"}
        }
    )
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Требуется JWT-аутентификация"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            alerts = AlertData.objects.select_related('camera').only(
                "id", "first_detection_datetime", "last_detection_datetime", "camera_id"
            ).order_by('-created_at')

            results = self.paginate_queryset(alerts, request, view=self)
            serializer = self.serializer_class(results, many=True)
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            logging.error(f"Ошибка получения данных: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Создать новый alert",
        description="Требует Token в заголовке запроса. Создаёт новый alert, привязывая его к камере.",
        request=AlertDataSerializer,
        responses={
            201: AlertDataSerializer,
            400: {"description": "Ошибка запроса"},
            401: {"description": "Отсутствует или неверный Token"},
            404: {"description": "Камера не найдена"}
        }
    )
    def post(self, request):
        try:
            alert_data = request.data
            camera_id = alert_data.get("camera_id")

            if not camera_id:
                logging.warning("Ошибка: в запросе отсутствует 'camera_id'")
                return Response(
                    {"error": "Поле 'camera_id' обязательно"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            camera = Camera.objects.filter(id=camera_id).first()
            if not camera:
                logging.warning(f"Ошибка: камера с id={camera_id} не найдена")
                return Response(
                    {"error": f"Камера с id: {camera_id} не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )

            first_detection = alert_data.get("first_detection_datetime")
            last_detection = alert_data.get("last_detection_datetime")
            image_path = alert_data.get("image")

            try:
                alert = create_alert_safely(
                    camera=camera,
                    message=alert_data.get("message", "No message"),
                    first_detection_datetime=first_detection,
                    last_detection_datetime=last_detection,
                    image=image_path
                )
            except Exception as e:
                logging.error(f"Ошибка при создании алерта: {str(e)}", exc_info=True)
                return Response({"error": "Ошибка при сохранении данных"}, status=500)

            serializer = self.serializer_class(alert)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logging.error(f"Непредвиденная ошибка при обработке запроса: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            
class AlertDataDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AlertDataSerializer


    def get_object(self, pk):
        try:
            return AlertData.objects.get(pk=pk)
        except AlertData.DoesNotExist:
            raise Http404


    @extend_schema(
        summary="Получить alert по ID",
        description="Получить данные alert по его ID.",
        responses={
            200: AlertDataSerializer,
            400: {"описание": "ошибка запроса"},
            404: {"описание": "Alert не найден"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def get(self, request, pk):
        try:
            alert = self.get_object(pk)
            serializer = self.serializer_class(alert)
            return Response(serializer.data)
        except Http404:
            logging.warning(f"Alert с id: {pk} не найден")
            return Response({"ошибка": "Alert не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error(f"непредвиденная ошибка: {str(e)}", exc_info=True)
            return Response({"ошибка": f"непредвиденная ошибка: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Обновить данные alert по ID",
        description="Обновить данные alert по его ID.",
        request=AlertDataSerializer,
        responses={
            200: AlertDataSerializer,
            400: {"описание": "ошибка запроса"},
            404: {"описание": "Alert не найден"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def put(self, request, pk):
        try:
            alert = self.get_object(pk)
            serializer = self.serializer_class(alert, data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                logging.warning(f"неверные данные для alert {pk}: {serializer.errors}")
                return Response({"ошибка": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            logging.warning(f"Alert с id: {pk} не найден")
            return Response({"ошибка": "Alert не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error(f"непредвиденная ошибка: {str(e)}", exc_info=True)
            return Response({"ошибка": f"непредвиденная ошибка: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @extend_schema(
        summary="Частичное обновление alert по ID",
        description="Частичное обновление данных alert по его ID.",
        request=AlertDataSerializer,
        responses={
            200: AlertDataSerializer,
            400: {"описание": "ошибка запроса"},
            404: {"описание": "Alert не найден"},
            500: {"описание": "ошибка сервера"}
        }
    )
    def patch(self, request, pk):
        try:
            alert = self.get_object(pk)
            serializer = self.serializer_class(alert, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                logging.warning(f"неверные данные для alert {pk}: {serializer.errors}")
                return Response({"ошибка": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            logging.warning(f"Alert с id: {pk} не найден")
            return Response({"ошибка": "Alert не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error(f"непредвиденная ошибка: {str(e)}", exc_info=True)
            return Response({"ошибка": f"непредвиденная ошибка: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
