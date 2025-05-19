
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from api.configs.logger import setup_logging
setup_logging()
import logging
from rest_framework import status
from drf_spectacular.utils import extend_schema

# health check <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Проверка состояния системы",
        description="Возвращает статус работы сервера.",
        responses={
            200: {
                "description": "Сервер работает нормально",
                "content": {
                    "application/json": {
                        "type": "object",
                        "example": {"health-check status": "ok"}
                    }
                }
            }
        }
    )
    def get(self, request):
        logging.debug(f"запрос по адресу /api/v1/health-check/")
        return Response({"health-check status": "ok"}, status=status.HTTP_200_OK)
# health check >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
