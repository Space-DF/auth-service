#!/bin/ash

python manage.py collectstatic --noinput

echo "Apply database migrations"
python manage.py migrate_smart || exit 1

echo "Starting server"
gunicorn --worker-class gevent --bind 0.0.0.0:80 --access-logfile - auth_service.wsgi & celery -A auth_service worker -l info -c 1
