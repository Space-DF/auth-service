#!/bin/bash

echo "Apply database migrations"
python manage.py migrate_schemas --shared

echo "Starting server"
gunicorn --bind 0.0.0.0:80 --access-logfile - auth_service.wsgi
