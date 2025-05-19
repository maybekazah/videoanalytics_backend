from api.configs.logger import setup_logging
import logging
import json
import redis
from api.configs.app import redis_client
setup_logging()
from api.metaclasses.singletone import Singletone


class RedisService(metaclass=Singletone):
    def __init__(self):
        try:
            self.redis_client = redis_client
            self.redis_client.ping()
            logging.info(f"инициализация RedisService")
        except redis.exceptions.ConnectionError:
            logging.error("Ошибка: не удалось подключиться к Redis. Проверьте, запущены ли контейнеры nn.")
            self.redis_client = None


    def get_redis_client(self) -> redis.Redis:
        return self.redis_client


    def get_data(self, container_id):
        try:
            self.data_key = f"nn_data_{container_id}"
            self.frame_base64_key = f"nn_frame_base64_{container_id}"
            self.thumbnail_base64_key = f"nn_thumbnail_base64_{container_id}"
            self.full_data_key = f"nn_full_data_{container_id}"
            
            data = self.redis_client.get(self.full_data_key)
            
            if not data:
                return None
            return json.loads(data)
            
        except (AttributeError, TypeError) as e:
            logging.error(f"Redis configuration error: {str(e)}")
            return None
            
        except json.JSONDecodeError as e:
            logging.error(f"Redis: invalid JSON data: {str(e)}")
            return None
            
        except redis.exceptions.RedisError as e:
            logging.error(f"Redis error: {str(e)}")
            return None
        
    def get_alert_data(self, container_id):
        try:
            self.alert_data_key = f"only_alert_status_data_{container_id}"
            data = self.redis_client.get(self.alert_data_key)
            if not data:
                return None
            return json.loads(data)
            
        except (AttributeError, TypeError) as e:
            logging.error(f"Redis configuration error: {str(e)}")
            return None
            
        except json.JSONDecodeError as e:
            logging.error(f"Redis: invalid JSON data: {str(e)}")
            return None
            
        except redis.exceptions.RedisError as e:
            logging.error(f"Redis error: {str(e)}")
            return None
        

    def get_thumbnail_data(self, container_id):
        try:
            self.thhumbnail_data_key = f"only_thumbnail_data_{container_id}"
            data = self.redis_client.get(self.thhumbnail_data_key)
            if not data:
                return None
            return json.loads(data)
            
        except (AttributeError, TypeError) as e:
            logging.error(f"Redis configuration error: {str(e)}")
            return None
            
        except json.JSONDecodeError as e:
            logging.error(f"Redis: invalid JSON data: {str(e)}")
            return None
            
        except redis.exceptions.RedisError as e:
            logging.error(f"Redis error: {str(e)}")
            return None    
        

    def get_frame_data(self, container_id):
        try:
            self.frame_data_key = f"only_frame_data_{container_id}"
            data = self.redis_client.get(self.frame_data_key)
            if not data:
                return None
            return json.loads(data)
            
        except (AttributeError, TypeError) as e:
            logging.error(f"Redis configuration error: {str(e)}")
            return None
            
        except json.JSONDecodeError as e:
            logging.error(f"Redis: invalid JSON data: {str(e)}")
            return None
            
        except redis.exceptions.RedisError as e:
            logging.error(f"Redis error: {str(e)}")
            return None    


    def send_data(self, data, camera_id):
        key = f"params_data_{camera_id}"
        if data is None:
            return {"message": "нет данных для отправки"}
        try:
            self.redis_client.set(key, json.dumps(data))
            return {
                "message": "данные успешно отправлены",
                "data": data
            }
        except Exception as e:
            return {"error": f"ошибка при отправке данных: {str(e)}"}