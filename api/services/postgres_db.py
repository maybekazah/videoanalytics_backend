from django.db import transaction
from api.models import AlertData

@transaction.atomic
def create_alert_safely(**kwargs):
    last_alert = AlertData.objects.select_for_update().order_by('-number').first()
    next_number = (last_alert.number + 1) if last_alert and last_alert.number is not None else 1

    alert = AlertData.objects.create(number=next_number, **kwargs)
    return alert