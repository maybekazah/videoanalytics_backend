from django.urls import re_path
from api.providers.provider import Provider

websocket_service = Provider.get_websocket_service()
alert_websocket_service = Provider.get_alert_websocket_service()
frame_websocket_service = Provider.get_frame_websocket_service()
thumbnail_websocket_service = Provider.get_thumbnail_websocket_service()

websocket_urlpatterns = [
    re_path(r"ws/get-data/$", websocket_service.as_asgi()),
    re_path(r"ws/get-alert-data/$", alert_websocket_service.as_asgi()),
    re_path(r"ws/get-frame-data/$", frame_websocket_service.as_asgi()),
    re_path(r"ws/get-thumbnail-data/$", thumbnail_websocket_service.as_asgi()),
]
