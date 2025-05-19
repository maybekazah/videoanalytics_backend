

from django.urls import path

from api.views.camera_settings import (
    CameraSettingsView,
    CameraSettingsDetailView
)

from api.views.cameras import (
    CameraView,
    CameraDetailView
)

from api.views.alerts import (
    AlertDataView,
    AlertDataDetailView
)

from api.views.health_check import (
    HealthCheckView
)

from api.views.redis import (
    RedisGetDataView,
    SendToNNRedisView
)

from api.views.auth import (
    LoginAPIView, 
    LogoutAPIView, 
    AuthenticatedTokenRefreshView,
    AuthCheckAPIView
)

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # auth
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', AuthenticatedTokenRefreshView.as_view(), name='token-refresh'),
    path('auth-check/', AuthCheckAPIView.as_view(), name='auth-check'),
    

    # health check
    path('health-check/', HealthCheckView.as_view(), name='health-check'),


    # redis
    path('redis/get-data/', RedisGetDataView.as_view(), name='redis-get'),


    path('alerts/', AlertDataView.as_view(), name='alerts'),  # GET, POST
    path('alerts/<int:pk>/', AlertDataDetailView.as_view(), name='alert-detail'),  # GET, PUT, PATCH, DELETE


    # Список всех камер и создание новой
    path('cameras/', CameraView.as_view(), name='cameras'),
    # Получение, обновление и удаление конкретной камеры
    path('cameras/<int:pk>/', CameraDetailView.as_view(), name='camera-detail'),


    # Список всех настроек и создание новых
    path('camera-settings/', CameraSettingsView.as_view(), name='camera-settings-list'),
    # Получение, обновление и удаление конкретных настроек
    path('camera-settings/<int:pk>/', CameraSettingsDetailView.as_view(), name='camera-settings-detail'),


    # маршрут для отправки данных в нейронки
    path('redis-send/', SendToNNRedisView.as_view(), name='redis-send'),


    # маршруты для документации openapi
    # Маршрут для получения схемы OpenAPI в формате JSON
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI для документации
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # ReDoc для документации
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
