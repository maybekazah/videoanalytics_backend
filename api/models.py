from django.db import models
from django.contrib.auth.models import User


class Camera(models.Model):
    camera_ip = models.CharField(max_length=200)
    camera_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Camera {self.camera_number} ({self.camera_ip})"


class DefaultCameraSettings(models.Model):
    camera = models.ForeignKey(
    Camera,
    on_delete=models.CASCADE, 
    related_name='default_camera_settings'
    )
    settings = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"DefaultCameraSettings {self.camera_number} ({self.camera_ip} {self.settings})"


class CameraSettings(models.Model):
    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE, 
        related_name='camera_settings'
    )
    settings = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CameraSettings {self.camera_number} ({self.camera_ip} {self.settings})"


class AlertData(models.Model):
    number = models.BigIntegerField(
        blank=True,
        null=True,
        db_index=True,
        help_text="номер обнаружения"
    )

    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='alerts', db_index=True)
    message = models.JSONField()
    first_detection_datetime = models.DateTimeField(null=True, blank=True, db_index=True)
    last_detection_datetime = models.DateTimeField(null=True, blank=True, db_index=True)
    image = models.TextField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return f"Alert from {self.camera} at {self.created_at}"


class VideoData(models.Model):
    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE, 
        related_name='videos' 
    )
    alert = models.ForeignKey(
        AlertData,
        on_delete=models.CASCADE,
        related_name='videos',
        help_text="Связанное оповещение"
    )
    path = models.CharField(
        max_length=255,
        help_text="Путь к видеофайлу"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Video Data'
        verbose_name_plural = 'Video Data'

    def __str__(self):
        return f"Video for Alert {self.alert_data.id} from Camera {self.camera.camera_number}"


class AdminSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_settings'
    )
    settings = models.JSONField(
        default=dict,
        help_text="Настройки администратора в формате JSON"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Admin Settings'
        verbose_name_plural = 'Admin Settings'

    def __str__(self):
        return f"Settings for {self.user.username}"


class UserSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_settings'
    )
    settings = models.JSONField(
        default=dict,
        help_text="Настройки обычного пользователя в формате JSON"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'

    def __str__(self):
        return f"Settings for {self.user.username}"
    
