FROM python:3.10-alpine AS builder

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache \
    build-base \
    libffi-dev \
    git

WORKDIR /install

RUN --mount=type=secret,id=github_token \
    pip install --no-cache-dir --prefix=/install \
    git+https://$(cat /run/secrets/github_token)@github.com/Space-DF/django-common-utils.git@dev

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE="auth_service.settings"

RUN apk add --no-cache \
    curl \
    libffi

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

RUN ["chmod", "+x", "./docker-entrypoint.sh"]

# Run the production server
ENTRYPOINT ["./docker-entrypoint.sh"]
