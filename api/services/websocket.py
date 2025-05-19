

from api.configs.logger import setup_logging
setup_logging()
import logging

from datetime import datetime, timedelta

import os
import json
import time
import logging
import asyncio
from typing import Dict, Any, Optional

from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken, TokenError


class WebSocketService(AsyncWebsocketConsumer):
    """
    Сервис для работы с WebSocket подключениями.
    Реализует паттерн Singleton для общего состояния между всеми подключениями.
    Аутентификация происходит через access_token в cookies.
    """

    _redis_service = None
    _clients: Dict[int, Dict[str, Any]] = {}
    _initialized = False
    _cleanup_started = False 

    def __init__(self, redis_service=None):
        super().__init__()
        if not WebSocketService._initialized and redis_service is not None:
            WebSocketService._redis_service = redis_service
            WebSocketService._initialized = True
            logging.info("WebSocketService инициализирован")

        self.client_id: Optional[int] = None
        self.camera_list: list = []
        self.data_task: Optional[asyncio.Task] = None
        self.is_running: bool = False

    @classmethod
    def get_redis_service(cls):
        return cls._redis_service

    async def connect(self):
        try:
            headers = dict(self.scope.get("headers", []))
            cookie_header = headers.get(b'cookie', b'').decode('utf-8')
            access_token = self.get_cookie_value(cookie_header, 'access_token')

            if not access_token or not self.authenticate_token(access_token):
                logging.warning(f"WebSocket-подключение отклонено: неверный токен")
                await self.send(json.dumps({"error": "403 Forbidden: Invalid token"}))
                await self.close(code=403)
                return

            self.client_id = id(self)
            WebSocketService._clients[self.client_id] = {
                'connection': self,
                'camera_list': [],
                'is_active': True,
                'last_ping': datetime.utcnow()
            }

            await self.accept()
            logging.info(f"Новое WebSocket подключение (ID: {self.client_id}). "
                         f"Всего подключений: {len(WebSocketService._clients)}")

            # 🧹 Запускаем фоновую задачу очистки
            if not WebSocketService._cleanup_started:
                asyncio.create_task(self._cleanup_inactive_clients())
                WebSocketService._cleanup_started = True

        except Exception as e:
            logging.error(f"Ошибка при подключении: {e}")
            await self.close()

    def get_cookie_value(self, cookie_header, cookie_name):
        cookies = dict(item.split("=", 1) for item in cookie_header.split("; ") if "=" in item)
        return cookies.get(cookie_name)

    def authenticate_token(self, token):
        try:
            AccessToken(token)
            return True
        except TokenError:
            logging.warning("Токен недействителен или истек")
            return False
        except Exception as e:
            logging.error(f"Ошибка проверки токена: {e}")
            return False

    async def disconnect(self, close_code):
        try:
            if self.client_id in WebSocketService._clients:
                self.is_running = False
                if self.data_task:
                    self.data_task.cancel()
                    try:
                        await self.data_task
                    except asyncio.CancelledError:
                        pass
                del WebSocketService._clients[self.client_id]
                logging.info(f"WebSocket отключен (ID: {self.client_id}). "
                             f"Осталось подключений: {len(WebSocketService._clients)}")
        except Exception as e:
            logging.error(f"Ошибка при отключении клиента {self.client_id}: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            # 🔄 Если это ping — просто обновляем last_ping и ничего больше не делаем
            if data.get("type") == "ping":
                WebSocketService._clients[self.client_id]['last_ping'] = datetime.utcnow()
                return

            # 🔄 Обновляем время последнего пинга
            WebSocketService._clients[self.client_id]['last_ping'] = datetime.utcnow()

            # 🔁 Обновляем список камер
            self.camera_list = data.get("camera_list", [])
            WebSocketService._clients[self.client_id]['camera_list'] = self.camera_list

            logging.info(f"📩 Клиент {self.client_id} обновил список камер: {self.camera_list}")

            # 🚫 Не запускаем повторно, если таск уже есть
            if self.data_task and not self.data_task.done():
                self.is_running = False
                self.data_task.cancel()
                try:
                    await self.data_task
                except asyncio.CancelledError:
                    pass

            self.is_running = True
            self.data_task = asyncio.create_task(self._get_and_send_data())

        except json.JSONDecodeError:
            logging.error(f"Ошибка декодирования JSON: {text_data}")
        except Exception as e:
            logging.error(f"Ошибка обработки сообщения: {e}")

    async def _get_and_send_data(self):
        if not WebSocketService._redis_service:
            logging.error("Redis сервис не инициализирован")
            return

        interval = float(os.getenv('GET_DATA_FROM_REDIS_TO_SOCKET_SLEEP_TIME', 0.1))
        logging.info(f"Запуск получения данных для клиента {self.client_id}, камеры: {self.camera_list}")

        while self.is_running:
            try:
                if not self.camera_list:
                    await asyncio.sleep(interval)
                    continue

                data = {}
                for camera_id in self.camera_list:
                    redis_data = WebSocketService._redis_service.get_data(camera_id)
                    if redis_data:
                        key = next(iter(redis_data))
                        data.update(redis_data[key])

                if data:
                    await self._send_data(data)

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                logging.info(f"Получение данных остановлено для клиента {self.client_id}")
                break
            except Exception as e:
                logging.error(f"Ошибка получения/отправки данных для клиента {self.client_id}: {e}")
                self.is_running = False
                break

    async def _send_data(self, data: dict):
        try:
            await self.send(text_data=json.dumps({"data": data}))
        except Exception as e:
            logging.error(f"Ошибка отправки данных клиенту {self.client_id}: {e}")
            raise

    async def _cleanup_inactive_clients(self):
        """Периодически удаляет неактивных клиентов."""
        timeout = timedelta(seconds=30)
        check_interval = 5

        while True:
            now = datetime.utcnow()
            to_remove = []

            for client_id, info in list(WebSocketService._clients.items()):
                last_ping = info.get('last_ping', now)
                if now - last_ping > timeout:
                    to_remove.append(client_id)

            for client_id in to_remove:
                connection = WebSocketService._clients[client_id]['connection']
                try:
                    await connection.close(code=4001)
                except Exception as e:
                    logging.warning(f"Ошибка при закрытии клиента {client_id}: {e}")
                del WebSocketService._clients[client_id]
                logging.info(f"Удалён неактивный WebSocket-клиент (ID: {client_id})")

            await asyncio.sleep(check_interval)

