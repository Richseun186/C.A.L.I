from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Fallback to local SQLite for rapid local development, or Postgres when DATABASE_URL provided
if 'test' not in sys.argv:
    DATABASES = {
        'default': env.db('DATABASE_URL', default=f"sqlite:///{BASE_DIR}/db.sqlite3")
    }

# In local development, avoid requiring SSL
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
