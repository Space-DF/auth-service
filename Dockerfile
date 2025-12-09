FROM python:3.10-alpine
ENV PYTHONUNBUFFERED=1

# Allows docker to cache installed dependencies between builds
RUN apk add build-base libffi-dev curl
COPY ./auth-service/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./django-common-utils django-common-utils
RUN pip install ../django-common-utils

# Adds our application code to the image
COPY ./auth-service auth-service

WORKDIR /auth-service

EXPOSE 80

ENV DJANGO_SETTINGS_MODULE="auth_service.settings"

RUN ["chmod", "+x", "./docker-entrypoint.sh"]

# Run the production server
ENTRYPOINT ["./docker-entrypoint.sh"]
