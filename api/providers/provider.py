from api.services.redis import RedisService
from api.services.websocket import WebSocketService
from api.metaclasses.singletone import Singletone
from api.services.thumbnail_websocket import ThumbnailWebSocketService
from api.services.frame_websocket import FrameWebSocketService
from api.services.alert_websocket import AlertWebSocketService


class Provider(metaclass=Singletone):

    @staticmethod
    def get_postgres_db_repository():
        pass

    @staticmethod
    def get_redis_service() -> RedisService:
        return RedisService()

    @staticmethod
    def get_websocket_service() -> WebSocketService:
        return WebSocketService(RedisService())


    @staticmethod
    def get_alert_websocket_service() -> AlertWebSocketService:
        return AlertWebSocketService(RedisService())
    
    
    @staticmethod
    def get_frame_websocket_service() -> FrameWebSocketService:
        return FrameWebSocketService(RedisService())
    
    
    @staticmethod
    def get_thumbnail_websocket_service() -> ThumbnailWebSocketService:
        return ThumbnailWebSocketService(RedisService())