import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['*']),
)

# Load .env.local first if present (Neon CLI generated), then .env
env_local = os.path.join(BASE_DIR, '.env.local')
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_local):
    environ.Env.read_env(env_local)
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

SECRET_KEY = env('SECRET_KEY', default='django-insecure-cali-schools-portal-super-secret-key-2026')

DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd-party security and auditing
    'axes',
    'simple_history',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'storages',

    # CALI Schools Core Domain Apps
    'apps.accounts',
    'apps.academics',
    'apps.assessments',
    'apps.results',
    'apps.finance',
    'apps.portal',
    'apps.notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'apps.accounts.auth_backends.SchoolAuthBackend',
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-ng'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Fast, isolated test database when running 'manage.py test'
import sys
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }


# Session & Security Settings
SESSION_COOKIE_AGE = 1800  # 30 minutes inactivity timeout
SESSION_SAVE_EVERY_REQUEST = True

# Axes Configuration (Brute Force Lockout)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.5  # 30 minutes (0.5 hours)
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = 'portal/lockout.html'

# Paystack & Termii Configuration Defaults
PAYSTACK_PUBLIC_KEY = env('PAYSTACK_PUBLIC_KEY', default='pk_test_cali_dummy_key')
PAYSTACK_SECRET_KEY = env('PAYSTACK_SECRET_KEY', default='sk_test_cali_dummy_key')
TERMII_API_KEY = env('TERMII_API_KEY', default='')
TERMII_SENDER_ID = env('TERMII_SENDER_ID', default='CALISCHOOLS')

# Neon Platform Integrations
NEON_BRANCH = env('NEON_BRANCH', default='production')
NEON_BRANCH_ID = env('NEON_BRANCH_ID', default='')

# Neon Auth Configuration (Managed Better Auth / JWKS)
NEON_AUTH_BASE_URL = env('NEON_AUTH_BASE_URL', default='')
NEON_AUTH_JWKS_URL = env('NEON_AUTH_JWKS_URL', default='')

# Neon Object Storage (S3-compatible Lakebase Object Storage)
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default=None)
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default=None)
AWS_ENDPOINT_URL_S3 = env('AWS_ENDPOINT_URL_S3', default=None)
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default=env('NEON_STORAGE_BUCKET', default='assets'))
AWS_S3_REGION_NAME = env('AWS_REGION', default='eu-central-1')
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_ADDRESSING_STYLE = 'path'

if AWS_ENDPOINT_URL_S3 and AWS_ACCESS_KEY_ID:
    AWS_S3_ENDPOINT_URL = AWS_ENDPOINT_URL_S3
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "access_key": AWS_ACCESS_KEY_ID,
                "secret_key": AWS_SECRET_ACCESS_KEY,
                "endpoint_url": AWS_ENDPOINT_URL_S3,
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "signature_version": "s3v4",
                "addressing_style": "path",
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

