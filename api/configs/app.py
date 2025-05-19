# TODO сюда вынести все константы через os.getenv и потом из этого файла импортировать в другие файлы
import os
import redis
import json


# номер контейнера (=камеры) frame_collector реплики
CONTAINER_ID = os.getenv("CONTAINER_ID")


VIDEO_PATH = os.getenv(f'VIDEO_PATH_{CONTAINER_ID}')


DETECTION_MODEL_PATH = os.getenv('DETECTION_MODEL_PATH')
DETECTION_MODEL_CUDA_DEVICE = os.getenv('DETECTION_MODEL_CUDA_DEVICE')


# автоматический запуск видео с камер
# -----------------------------------
DEFAULT_RUN = os.getenv("DEFAULT_RUN", "True").lower() == "true"


# настройки для нейронной сети, уверенность и другие параметры
# ------------------------------------------------------------
DEFAULT_DETECTION_MODEL_IMGSZ = int(os.getenv(f'DEFAULT_DETECTION_MODEL_IMGSZ'))
DEFAULT_DETECTION_MODEL_CONF = float(os.getenv(f'DEFAULT_DETECTION_MODEL_CONF'))
DEFAULT_DETECTION_MODEL_IOU = float(os.getenv(f'DEFAULT_DETECTION_MODEL_IOU'))
DEFAULT_DETECTION_MODEL_HALF = os.getenv("DEFAULT_DETECTION_MODEL_HALF", "True").lower() == "true"


# настройки отрисовки детектируемых объектов и рамки периметра
# ------------------------------------------------------------
# отрисовывать ли вообще результаты
DEFAULT_DRAW_RESULT = os.getenv("DEFAULT_DRAW_RESULT", "True").lower() == "true"
DEFAULT_DRAW_DETECT_BOXES = os.getenv("DEFAULT_DRAW_DETECT_BOXES", "False").lower() == "true"
DEFAULT_DRAW_PERIMETER = os.getenv("DEFAULT_DRAW_PERIMETER", "False").lower() == "true"


# настройки для отображения для стандартной отрисовки через yolo ultralytics
# --------------------------------------------------------------------------
USE_ULTRALITYCS_PLOT_VISUALISATION_BOXES_AND_LABELS = os.getenv("USE_ULTRALITYCS_PLOT_VISUALISATION_BOXES_AND_LABELS", "True").lower() == "true"
DRAW_LABELS = os.getenv("DEFAULT_DRAW_RESULT", "True").lower() == "true"


# цвета контура детекции и рамки периметра
# ----------------------------------------
DRAW_LINE_THICKLESS = int(os.getenv("DRAW_LINE_THICKLESS", 16))
BOX_COLOR = tuple(map(int, os.getenv("BOX_COLOR", "255,0,0").split(',')))
COUNTOR_COLOR = tuple(map(int, os.getenv("COUNTOR_COLOR", "255,0,0").split(',')))


# настройки возвращаемых кадров и миниатюр камер на страницу интерфейса для фронтенда и их качество/сжатие
# --------------------------------------------------------------------------------------------------------
THUMBNAIL_SIZE = tuple(map(int, os.getenv("THUMBNAIL_SIZE", "1920,1080").split(',')))
FRAME_SIZE = tuple(map(int, os.getenv("FRAME_SIZE", "1920,1080").split(',')))
THUMBNAIL_QUALITY = int(os.getenv("THUMBNAIL_QUALITY", 100))
FRAME_QUALITY = int(os.getenv("FRAME_QUALITY", 100))


# настройки для контура границ детекции по кадру
# ----------------------------------------------
DAY_CONTOUR = json.loads(os.getenv(f'DAY_CONTOUR')) if os.getenv(f'DAY_CONTOUR') else [[0, 0], [1920, 0], [1920, 1080], [0, 1080]]
NIGHT_CONTOUR = json.loads(os.getenv(f'NIGHT_CONTOUR')) if os.getenv(f'NIGHT_CONTOUR') else [[0, 0], [1920, 0], [1920, 1080], [0, 1080]]
DEFAULT_CONTOUR = json.loads(os.getenv(f'DEFAULT_CONTOUR_{CONTAINER_ID}')) if os.getenv(f'DEFAULT_CONTOUR_{CONTAINER_ID}') else [[0, 0], [1920, 0], [1920, 1080], [0, 1080]]

USE_DAY_COUNTOR = os.getenv("USE_DAY_COUNTOR", "True").lower() == "true"
DAY_COUNTOR_TIME_START = tuple(map(int, os.getenv("DAY_COUNTOR_TIME_START", "12,00,00").split(',')))
DAY_COUNTOR_TIME_END = tuple(map(int, os.getenv("DAY_COUNTOR_TIME_END", "16,00,00").split(',')))

USE_NIGHT_COUNTOR = os.getenv("USE_NIGHT_COUNTOR", "True").lower() == "true"
NIGHT_COUNTOR_TIME_START = tuple(map(int, os.getenv("NIGHT_COUNTOR_TIME_START", "21,00,00").split(',')))
NIGHT_COUNTOR_TIME_END = tuple(map(int, os.getenv("NIGHT_COUNTOR_TIME_END", "8,00,00").split(',')))


# настройки пропуска кадров по отдельным кадрам или по времени
# ------------------------------------------------------------
# пропускать на обработку каждый N кадр
DEFAULT_SKIP_FRAME_COUNTER = int(os.getenv("DEFAULT_SKIP_FRAME_COUNTER", 1))


# включить пропуск по времени и время в секундах (пропускает на обработку один кадр в N секунд)
# с камеры и с видеофайла будет брать кадр раз в заданное время, без пропуска кадров
# по дефолту вообще не используется, а используется USE_TIME_PAUSE_FOR_PROCESSING_FRAME
FREEZE_FRAME_ENABLED = os.getenv("FREEZE_FRAME_ENABLED", "True").lower() == "true"
FREEZE_FRAME_TIME = float(os.getenv("FREEZE_FRAME_TIME", 0.0))


# записывать ли видеодетекции в файл (логика не реализована)
# ----------------------------------------------------------
DEFAULT_WRITE_VIDEO = os.getenv("DEFAULT_WRITE_VIDEO", "False").lower() == "true"


# сохранять обнаруженные объекты в бд, не более раз в n секунд
# ------------------------------------------------------------
DEFAULT_ALERT_SAVE_TIMEOUT = int(os.getenv("DEFAULT_ALERT_SAVE_TIMEOUT", 5))


# список детектируемых стандартных yolo классов
# ---------------------------------------------
DEFAULT_LIST_OF_DETECT_CLASSES = json.loads(os.getenv(f'DEFAULT_LIST_OF_DETECT_CLASSES_{CONTAINER_ID}')) if os.getenv(f'DEFAULT_LIST_OF_DETECT_CLASSES_{CONTAINER_ID}') else [0]


# детектировать ли вообще объекты, с пересечением с рамкой периметра (если задан False то алёрты срабатывают по всему кадру)
# --------------------------------------------------------------------------------------------------------------------------
DEFAULT_DETECT_WITH_INTERSECTION = os.getenv("DEFAULT_DETECT_WITH_INTERSECTION", "False").lower() == "true"


NN_LOGS = os.getenv('NN_LOGS')
NN_DEBUG = int(os.getenv('NN_DEBUG'))
DJANGO_LOGS = os.getenv('DJANGO_LOGS')
DJANGO_DEBUG = int(os.getenv('DJANGO_DEBUG'))


REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_DECODE_RESPONSES = bool(os.getenv('REDIS_DECODE_RESPONSES', 0))
REDIS_SOCKET_TIMEOUT = int(os.getenv('REDIS_SOCKET_TIMEOUT'))
REDIS_SOCKET_KEEPALIVE = bool(os.getenv('REDIS_SOCKET_KEEPALIVE'))
REDIS_HEALTH_CHECK_INTERVAL = int(os.getenv('REDIS_HEALTH_CHECK_INTERVAL'))
REDIS_POOL = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=REDIS_DECODE_RESPONSES,
    socket_keepalive=REDIS_SOCKET_KEEPALIVE,
    health_check_interval=REDIS_HEALTH_CHECK_INTERVAL,
)

redis_client = redis.Redis(connection_pool=REDIS_POOL)