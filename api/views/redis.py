
from api.configs.logger import setup_logging
setup_logging()
import logging

from drf_spectacular.utils import extend_schema

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.providers.provider import Provider

import redis
import json


# redis <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class RedisGetDataView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Получить данные из Redis по container_id",
        description="Метод для получения данных из Redis по идентификатору контейнера.",
        request=None,
        responses={
            200: {
                "description": "Данные успешно получены",
                "content": {
                    "application/json": {
                        "type": "object",
                        "example": {"data": "sample data"}
                    }
                }
            },
            400: {
                "description": "container_id не был передан",
                "content": {
                    "application/json": {
                        "type": "object",
                        "example": {"error": "container_id is required"}
                    }
                }
            },
            404: {
                "description": "Данные не найдены",
                "content": {
                    "application/json": {
                        "type": "object",
                        "example": {"error": "Data not found"}
                    }
                }
            },
            503: {
                "description": "Ошибка подключения к Redis",
                "content": {
                    "application/json": {
                        "type": "object",
                        "example": {"error": "Redis connection error"}
                    }
                }
            },
            500: {
                "description": "Ошибка Redis или ошибка при декодировании JSON",
                "content": {
                    "application/json": {
                        "type": "object",
                        "example": {"error": "Redis error"}
                    }
                }
            }
        }
    )
    
    def get(self, request):
        try:
            container_id = request.data.get("container_id")
            if not container_id:
                return Response(
                    {"error": "container_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = Provider.get_redis_service().get_data(container_id)
            
            if data is None:
                return Response(
                    {"error": "Data not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(data, status=status.HTTP_200_OK)

        except redis.exceptions.ConnectionError as e:
            logging.error(f"Ошибка подключения к Redis: {e}")
            return Response(
                {"error": "Redis connection error"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        except redis.exceptions.RedisError as e:
            logging.error(f"Ошибка Redis: {e}")
            return Response(
                {"error": "Redis error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except json.JSONDecodeError as e:
            logging.error(f"Ошибка декодирования JSON: {e}")
            return Response(
                {"error": "Invalid JSON data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logging.error(f"Непредвиденная ошибка: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# redis >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>



class SendToNNRedisView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Отправить данные в Redis",
        description="Отправляет данные для обработки в нейронную сеть через Redis.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "Данные, которые нужно отправить в Redis"
                    },
                    "camera_id": {
                        "type": "integer",
                        "description": "ID камеры, с которой связаны данные"
                    }
                },
                "required": ["data", "camera_id"],
                "example": {
                    "data": "sample data",
                    "camera_id": 1
                }
            }
        },
        responses={
            200: {
                "description": "Данные успешно отправлены в Redis",
                "content": {
                    "application/json": {
                        "type": "object",
                        "example": {"result": "Data sent successfully"}
                    }
                }
            },
            400: {
                "description": "Ошибка, если отсутствуют обязательные поля 'data' или 'camera_id'",
                "content": {
                    "application/json": {
                        "type": "object",
                        "example": {"error": "Необходимо указать data и camera_id"}
                    }
                }
            },
            500: {
                "description": "Внутренняя ошибка сервера",
                "content": {
                    "application/json": {
                        "type": "object",
                        "example": {"error": "Internal server error"}
                    }
                }
            }
        }
    )
    def post(self, request):
        try:
            data = request.data.get("data")
            camera_id = request.data.get("camera_id")
            
            if not data or not camera_id:
                return Response({
                    "error": "Необходимо указать data и camera_id"
                }, status=status.HTTP_400_BAD_REQUEST)

            result = Provider.get_redis_service().send_data(data, camera_id)
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
