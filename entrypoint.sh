#!/bin/bash

python manage.py migrate --no-input
python manage.py collectstatic --no-input

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin@gmail.com', 'admin@gmail.com', 'admin@123456')" | python manage.py shell

gunicorn config.wsgi:application -c sart_gunicorn.py
