from django.contrib import admin
from .models import Camera, CameraSettings, DefaultCameraSettings, AlertData, VideoData, AdminSettings, UserSettings

# Простая регистрация моделей
admin.site.register(Camera)
admin.site.register(CameraSettings)
admin.site.register(DefaultCameraSettings)
admin.site.register(AlertData)
admin.site.register(VideoData)
admin.site.register(AdminSettings)
admin.site.register(UserSettings)
