# Django сервис

FROM python:3.12.4

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=1 \
    PYTHONHASHSEED=0 

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx supervisor
    
# 🔹 Устанавливаем часовой пояс без интерактивного выбора
ENV TZ=Europe/Moscow
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

RUN pip install --upgrade pip

RUN pip install \
    psycopg2-binary==2.9.9 \
    gunicorn==23.0.0 \
    Django==5.1.6 \
    redis==5.2.1 \
    djangorestframework==3.15.2 \
    djangorestframework-simplejwt==5.4.0 \
    django-cors-headers==4.7.0 \
    Faker==36.1.1 \
    requests==2.32.3 \
    pytest==8.3.4 \
    rich==13.9.4 \
    channels==4.2.0 \
    daphne==4.1.2 \
    channels-redis==4.2.1 \ 
    unittest2==1.1.0 \
    django-extensions==3.2.3 \
    drf-spectacular==0.28.0

COPY . .

