from api.configs.logger import setup_logging
setup_logging()
import logging

import os
import json
import time
import logging
import asyncio
from typing import Dict, Any, Optional

from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken, TokenError


WEBSOCKET_CAMERA_LIST = json.loads(os.getenv(f'WEBSOCKET_CAMERA_LIST'))

class ThumbnailWebSocketService(AsyncWebsocketConsumer):
    """
    Сервис для работы с WebSocket подключениями.
    Реализует паттерн Singleton для общего состояния между всеми подключениями.
    Аутентификация происходит через access_token в cookies.
    """

    _redis_service = None
    _clients: Dict[int, Dict[str, Any]] = {}
    _initialized = False

    def __init__(self, redis_service=None):
        super().__init__()
        if not ThumbnailWebSocketService._initialized and redis_service is not None:
            ThumbnailWebSocketService._redis_service = redis_service
            ThumbnailWebSocketService._initialized = True
            logging.info("ThumbnailWebSocket инициализирован")

        self.client_id: Optional[int] = None
        self.camera_list: list = []
        self.data_task: Optional[asyncio.Task] = None
        self.is_running: bool = False

    @classmethod
    def get_redis_service(cls):
        return cls._redis_service

    async def connect(self):
        """Обработка нового подключения с проверкой JWT из cookies."""
        try:
            headers = dict(self.scope.get("headers", []))
            cookie_header = headers.get(b'cookie', b'').decode('utf-8')
            access_token = self.get_cookie_value(cookie_header, 'access_token')

            if not access_token or not self.authenticate_token(access_token):
                logging.warning(f"ThumbnailWebSocket-подключение отклонено: неверный токен")
                await self.send(json.dumps({"error": "403 Forbidden: Invalid token"}))
                await self.close(code=403)
                return

            self.client_id = id(self)
            ThumbnailWebSocketService._clients[self.client_id] = {
                'connection': self,
                'camera_list': [],
                'is_active': True
            }

            await self.accept()
            logging.info(f"Новое ThumbnailWebSocket подключение (ID: {self.client_id}). "
                         f"Всего подключений: {len(ThumbnailWebSocketService._clients)}")
        except Exception as e:
            logging.error(f"ThumbnailWebSocket Ошибка при подключении: {e}")
            await self.close()

    def get_cookie_value(self, cookie_header, cookie_name):
        """Извлекает значение cookie по имени из заголовка Cookie."""
        cookies = dict(item.split("=", 1) for item in cookie_header.split("; ") if "=" in item)
        return cookies.get(cookie_name)

    def authenticate_token(self, token):
        """Проверяет валидность JWT-токена."""
        try:
            AccessToken(token)
            return True
        except TokenError:
            logging.warning("ThumbnailWebSocket Токен недействителен или истек")
            return False
        except Exception as e:
            logging.error(f"ThumbnailWebSocket Ошибка проверки токена: {e}")
            return False

    async def disconnect(self, close_code):
        try:
            if self.client_id in ThumbnailWebSocketService._clients:
                self.is_running = False
                if self.data_task:
                    self.data_task.cancel()
                    try:
                        await self.data_task
                    except asyncio.CancelledError:
                        pass
                del ThumbnailWebSocketService._clients[self.client_id]
                logging.info(f"ThumbnailWebSocket отключен (ID: {self.client_id}). "
                             f"Осталось подключений: {len(ThumbnailWebSocketService._clients)}")
        except Exception as e:
            logging.error(f"ThumbnailWebSocket Ошибка при отключении клиента {self.client_id}: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            self.camera_list = WEBSOCKET_CAMERA_LIST
            # self.camera_list = data.get("camera_list")
            ThumbnailWebSocketService._clients[self.client_id]['camera_list'] = self.camera_list

            logging.info(f"ThumbnailWebSocket Клиент {self.client_id} обновил список камер (жестко заданы в коде): {self.camera_list}")

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
            logging.error(f"ThumbnailWebSocket Ошибка декодирования JSON: {text_data}")
        except Exception as e:
            logging.error(f"ThumbnailWebSocket Ошибка обработки сообщения: {e}")

    async def _get_and_send_data(self):
        if not ThumbnailWebSocketService._redis_service:
            logging.error("ThumbnailWebSocket Redis сервис не инициализирован")
            return

        interval = float(os.getenv('GET_DATA_FROM_REDIS_TO_SOCKET_SLEEP_TIME', 0.1))

        metrics = {
            'skipped_messages': 0,
            'sent_messages': 0,
            'last_metrics_log': time.time(),
            'start_time': time.time()
        }

        previous_data = None

        while self.is_running:
            try:
                latest_data = {}  # Новый словарь создается каждый раз
                if self.camera_list:
                    for camera_id in self.camera_list:
                        redis_data = ThumbnailWebSocketService._redis_service.get_thumbnail_data(camera_id)
                        if redis_data:
                            key = next(iter(redis_data))
                            latest_data.update(redis_data[key])

                    if latest_data and latest_data != previous_data:
                        if hasattr(self, 'transport') and self.transport:
                            if hasattr(self.transport, '_buffer'):
                                self.transport._buffer.clear()
                        
                        await self.send(text_data=json.dumps({"data": latest_data}))
                        previous_data = latest_data  # Без .copy(), так как latest_data - новый объект
                        metrics['sent_messages'] += 1
                    else:
                        metrics['skipped_messages'] += 1

                # Логирование метрик каждые 10 секунд
                current_time = time.time()
                if current_time - metrics['last_metrics_log'] >= 10:
                    uptime = current_time - metrics['start_time']
                    avg_send_rate = metrics['sent_messages'] / uptime if uptime > 0 else 0
                    skip_ratio = (metrics['skipped_messages'] /
                                  (metrics['sent_messages'] + metrics['skipped_messages']) * 100
                                  if metrics['sent_messages'] + metrics['skipped_messages'] > 0 else 0)

                    logging.info(
                        f"ThumbnailWebSocket Метрики клиента {self.client_id}:\n"
                        f"  ├─ Время работы: {uptime:.1f} сек\n"
                        f"  ├─ Отправлено: {metrics['sent_messages']}\n"
                        f"  ├─ Пропущено: {metrics['skipped_messages']}\n"
                        f"  ├─ Частота отправки: {avg_send_rate:.1f} сообщ/сек\n"
                        f"  └─ Процент пропусков: {skip_ratio:.1f}%"
                    )
                    metrics['last_metrics_log'] = current_time

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                uptime = time.time() - metrics['start_time']
                logging.info(
                    f"ThumbnailWebSocket Остановка клиента {self.client_id}. Итоговые метрики:\n"
                    f"  ├─ Время работы: {uptime:.1f} сек\n"
                    f"  ├─ Всего отправлено: {metrics['sent_messages']}\n"
                    f"  └─ Всего пропущено: {metrics['skipped_messages']}"
                )
                break
            except Exception as e:
                logging.error(f"ThumbnailWebSocket Ошибка получения/отправки данных для клиента {self.client_id}: {e}")
                self.is_running = False
                break 