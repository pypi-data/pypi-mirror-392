"""Middlewares para frameworks"""

from seguridad_nacional.middleware.fastapi_middleware import SecurityMiddleware as FastAPISecurityMiddleware
from seguridad_nacional.middleware.flask_middleware import FlaskSecurityMiddleware
from seguridad_nacional.middleware.django_middleware import DjangoSecurityMiddleware

__all__ = [
    "FastAPISecurityMiddleware",
    "FlaskSecurityMiddleware",
    "DjangoSecurityMiddleware",
]

