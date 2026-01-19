FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE="auth_service.settings"

# Allow passing GITHUB_TOKEN as build arg for local builds
ARG GITHUB_TOKEN

RUN apk add --no-cache \
    build-base \
    libffi-dev \
    curl \
    git

# Configure git to use GITHUB_TOKEN for private repo access (only if token is provided)
RUN if [ -n "$GITHUB_TOKEN" ]; then \
        git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"; \
    fi

RUN pip install --no-cache-dir \
    git+https://github.com/Space-DF/django-common-utils.git@dev

COPY . .
WORKDIR /app

RUN pip install -r requirements.txt

RUN ["chmod", "+x", "./docker-entrypoint.sh"]

# Run the production server
ENTRYPOINT ["./docker-entrypoint.sh"]
