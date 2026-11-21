# Production Dockerfile for CALI Schools on Render
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# Install system dependencies required for WeasyPrint & PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu-core \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/

# Collect static assets
RUN python manage.py collectstatic --noinput --settings=config.settings.production || true

EXPOSE 8000

# Start script: apply migrations, seed catalog, and launch Gunicorn
CMD python manage.py migrate --noinput && \
    python manage.py seed_cali_school && \
    python manage.py seed_nigerian_subject_bank && \
    gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers 3 --timeout 120
