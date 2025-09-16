from .base import *


DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS += [
    "debug_toolbar"
]

INTERNAL_IPS = [
    "127.0.0.1"
]

MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")