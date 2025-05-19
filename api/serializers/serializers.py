from rest_framework import serializers
from api.models import AlertData, Camera, CameraSettings


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ['id', 'camera_number', 'camera_ip']
        read_only_fields = ['created_at', 'updated_at']
        

class AlertDataSerializer(serializers.ModelSerializer):
    camera = CameraSerializer(read_only=True)
    
    class Meta:
        model = AlertData
        fields = ['id', 'number', 'camera', 'message', 'first_detection_datetime', 
                 'last_detection_datetime', 'image']
        read_only_fields = ['created_at', 'updated_at']



class CameraSettingsSerializer(serializers.ModelSerializer):
    camera_id = serializers.PrimaryKeyRelatedField(
        queryset=Camera.objects.all(), write_only=True, source="camera"
    )

    settings = serializers.JSONField()

    class Meta:
        model = CameraSettings
        fields = ['id', 'camera_id', 'settings', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_settings(self, value):
        """
        Валидация JSON-поля settings: проверяем, что все обязательные ключи присутствуют.
        """
        required_fields = [
            "run", "camera_id", "video_path", "alert_save_timeout", 
            "skip_frame_counter", "detect_with_perimeter_intersection", 
            "draw_result", "draw_detect_boxes", "draw_perimeter", 
            "freeze_frame_enabled", "freeze_frame_time_seconds", 
            "detection_model_half", "detection_model_imgsz", 
            "detection_model_iou", "detection_model_conf", 
            "list_of_detect_classes", "contour_points_list", 
            "day_contour", "night_contour"
        ]

        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")

        if not isinstance(value["list_of_detect_classes"], list):
            raise serializers.ValidationError("list_of_detect_classes must be a list.")

        for field in ["contour_points_list", "day_contour", "night_contour"]:
            if not isinstance(value[field], list) or not all(isinstance(i, list) for i in value[field]):
                raise serializers.ValidationError(f"{field} must be a list of lists.")

        return value
