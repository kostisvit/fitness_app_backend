# project/settings/production.py
import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "example.com",
    "www.example.com",
]

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

STATIC_ROOT = BASE_DIR / "staticfiles"
