FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE="auth_service.settings"

RUN apk add --no-cache \
    build-base \
    libffi-dev \
    curl \
    git

# Install private repo using BuildKit secret
RUN --mount=type=secret,id=github_token \
    pip install --no-cache-dir \
    git+https://x-access-token:$(cat /run/secrets/github_token)@github.com/Space-DF/django-common-utils.git@dev


COPY . .
WORKDIR /app

RUN pip install -r requirements.txt

RUN ["chmod", "+x", "./docker-entrypoint.sh"]

# Run the production server
ENTRYPOINT ["./docker-entrypoint.sh"]
