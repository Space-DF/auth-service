FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE="auth_service.settings"

RUN apk add --no-cache \
    build-base \
    libffi-dev \
    curl \
    git

# Configure git to use GITHUB_TOKEN for private repo access
RUN git config --global credential.helper store && \
    git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"

RUN pip install --no-cache-dir \
    git+https://github.com/Space-DF/django-common-utils.git@dev

COPY . .
WORKDIR /app

RUN pip install -r requirements.txt

RUN ["chmod", "+x", "./docker-entrypoint.sh"]

# Run the production server
ENTRYPOINT ["./docker-entrypoint.sh"]
