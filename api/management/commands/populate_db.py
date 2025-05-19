from django.core.management.base import BaseCommand
from api.models import Camera, CameraSettings
from copy import deepcopy

# Фиксированные данные для всех камер
DEFAULT_CAMERA_IP = "192.168.1.100"  # Один и тот же IP (можно изменить)
DEFAULT_VIDEO_PATH = "test/video.mp4"  # Один и тот же путь

# Шаблон настроек (как в вашем коде)
DEFAULT_SETTINGS_TEMPLATE = {
    "camera_id": 0,
    "data": {
        "run": True,
        "camera_id": 0,
        "video_path": DEFAULT_VIDEO_PATH,
        "alert_save_timeout": 10,
        "skip_frame_counter": 5,
        "detect_with_perimeter_intersection": True,
        "draw_result": True,
        "draw_detect_boxes": True,
        "draw_perimeter": True,
        "freeze_frame_enabled": False,
        "detection_model_half": False,
        "detection_model_imgsz": 640,
        "detection_model_iou": 0.45,
        "detection_model_conf": 0.25,
        "freeze_frame_time_seconds": 5,
        "list_of_detect_classes": [0, 1, 2],  # Пример классов (можно изменить)
        "contour_points_list": [[0, 0], [100, 0], [100, 100], [0, 100]],  # Пример контура
        "day_contour": [[10, 10], [90, 10], [90, 90], [10, 90]],
        "night_contour": [[20, 20], [80, 20], [80, 80], [20, 80]],
        "countour_color": [0, 255, 0],
        "box_color": [255, 0, 0],
        "draw_line_thickless": 2,
        "frame_quality": 90,
        "thumbnail_quality": 70,
        "thumbnail_size": [320, 180],
        "frame_size": [1920, 1080],
        "draw_labels": True,
        "use_day_countour": True,
        "use_night_countour": True,
        "day_countour_time_start": "06:00",
        "day_countour_time_end": "18:00",
        "night_countour_time_start": "18:00",
        "night_countour_time_end": "06:00",
    }
}

class Command(BaseCommand):
    help = "Создает 30 одинаковых камер с одинаковыми настройками"

    def handle(self, *args, **kwargs):
        total_cameras = 30

        for i in range(1, total_cameras + 1):
            # Создаем или обновляем камеру
            camera, created = Camera.objects.get_or_create(
                camera_number=i,
                defaults={"camera_ip": f"{DEFAULT_CAMERA_IP}"}  # Можно добавить ":i" для уникальности
            )
            self.stdout.write(f"{'Создана' if created else 'Обновлена'} камера #{i} (IP: {camera.camera_ip})")

            # Готовим настройки
            settings = deepcopy(DEFAULT_SETTINGS_TEMPLATE)
            settings["camera_id"] = i
            settings["data"]["camera_id"] = i

            # Создаем или обновляем настройки камеры
            CameraSettings.objects.update_or_create(
                camera=camera,
                defaults={"settings": settings}
            )
            self.stdout.write(f"✅ Настройки для камеры #{i} применены")

        self.stdout.write(self.style.SUCCESS(f"Успешно создано/обновлено {total_cameras} камер!"))