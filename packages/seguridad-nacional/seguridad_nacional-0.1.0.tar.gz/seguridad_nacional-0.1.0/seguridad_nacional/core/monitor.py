"""Funciones para monitorear aplicaciones"""

import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


def _is_fastapi(app) -> bool:
    """Verificar si la aplicación es FastAPI"""
    try:
        from fastapi import FastAPI
        return isinstance(app, FastAPI)
    except ImportError:
        return False


def _is_flask(app) -> bool:
    """Verificar si la aplicación es Flask"""
    try:
        from flask import Flask
        return isinstance(app, Flask)
    except ImportError:
        return False


def _is_django(app) -> bool:
    """Verificar si la aplicación es Django (por configuración)"""
    # Django no pasa la app directamente, se detecta por configuración
    try:
        import django
        from django.conf import settings
        return hasattr(settings, 'SECRET_KEY')
    except ImportError:
        return False
    except:
        return False


def monitor(app=None, config_path: Optional[str] = None, framework: Optional[str] = None):
    """
    Monitorear una aplicación web automáticamente (detecta el framework)
    
    Soporta:
    - FastAPI
    - Flask
    - Django (requiere configuración en settings.py)
    
    Args:
        app: Aplicación (FastAPI o Flask). Para Django, puede ser None.
        config_path: Ruta al archivo de configuración (opcional)
        framework: Framework específico ('fastapi', 'flask', 'django'). 
                   Si es None, se detecta automáticamente.
    
    Ejemplos:
        # FastAPI
        from fastapi import FastAPI
        app = FastAPI()
        sn.monitor(app)
        
        # Flask
        from flask import Flask
        app = Flask(__name__)
        sn.monitor(app)
        
        # Django (en settings.py)
        MIDDLEWARE = [
            'seguridad_nacional.middleware.django_middleware.DjangoSecurityMiddleware',
            ...
        ]
    """
    # Detectar framework automáticamente si no se especifica
    if framework is None:
        if app is not None:
            if _is_fastapi(app):
                framework = 'fastapi'
            elif _is_flask(app):
                framework = 'flask'
            else:
                # Intentar detectar Django
                if _is_django(None):
                    framework = 'django'
                else:
                    raise TypeError(
                        f"Framework no soportado o no detectado. "
                        f"Tipo de aplicación: {type(app)}. "
                        f"Frameworks soportados: FastAPI, Flask, Django"
                    )
    else:
        framework = framework.lower()
    
    # Llamar a la función específica del framework
    if framework == 'fastapi':
        return _monitor_fastapi(app, config_path)
    elif framework == 'flask':
        return _monitor_flask(app, config_path)
    elif framework == 'django':
        return _monitor_django(app, config_path)
    else:
        raise ValueError(f"Framework no válido: {framework}. Use 'fastapi', 'flask' o 'django'")


def _monitor_fastapi(app, config_path: Optional[str] = None):
    """Monitorear aplicación FastAPI"""
    try:
        from fastapi import FastAPI
        from seguridad_nacional.middleware.fastapi_middleware import SecurityMiddleware
        from seguridad_nacional.core.security_manager import get_manager
        from seguridad_nacional.config.settings import get_settings
        
        # Verificar que es una aplicación FastAPI
        if not isinstance(app, FastAPI):
            raise TypeError("La aplicación debe ser una instancia de FastAPI")
        
        # Obtener configuración (usar config_path si se proporciona)
        from seguridad_nacional.config.settings import load_settings_from_file
        if config_path:
            settings = load_settings_from_file(config_path)
        else:
            settings = get_settings()
        
        if not settings.enabled:
            logger.info("Seguridad Nacional deshabilitada")
            return
        
        # Inicializar el gestor
        manager = get_manager(config_path)
        
        # Agregar middleware
        app.add_middleware(SecurityMiddleware, config_path=config_path)
        
        # Agregar rutas del dashboard si está habilitado
        if settings.dashboard_enabled:
            from seguridad_nacional.dashboard.routes import setup_dashboard_routes
            logger.info(f"Configurando dashboard en {settings.dashboard_path}")
            setup_dashboard_routes(app, manager, settings)
            logger.info(f"Dashboard configurado correctamente en {settings.dashboard_path}/dashboard")
        
        logger.info("Aplicación FastAPI monitoreada con Seguridad Nacional")
    
    except ImportError as e:
        logger.error(f"Error importando FastAPI: {e}")
        raise ImportError("FastAPI no está instalado. Instala con: pip install fastapi")
    except Exception as e:
        logger.error(f"Error monitoreando aplicación FastAPI: {e}")
        raise


def _monitor_flask(app, config_path: Optional[str] = None):
    """Monitorear aplicación Flask"""
    try:
        from flask import Flask
        from seguridad_nacional.middleware.flask_middleware import FlaskSecurityMiddleware
        from seguridad_nacional.config.settings import get_settings
        
        # Verificar que es una aplicación Flask
        if not isinstance(app, Flask):
            raise TypeError("La aplicación debe ser una instancia de Flask")
        
        # Obtener configuración
        from seguridad_nacional.config.settings import load_settings_from_file
        if config_path:
            settings = load_settings_from_file(config_path)
        else:
            settings = get_settings()
        
        if not settings.enabled:
            logger.info("Seguridad Nacional deshabilitada")
            return
        
        # Agregar middleware
        FlaskSecurityMiddleware(app, config_path=config_path)
        
        # Agregar rutas del dashboard si está habilitado
        # Nota: Dashboard para Flask aún no está implementado completamente
        if settings.dashboard_enabled:
            logger.warning(
                "Dashboard para Flask aún no está completamente implementado. "
                "Usa FastAPI para acceso completo al dashboard."
            )
            # TODO: Implementar setup_flask_dashboard_routes
        
        logger.info("Aplicación Flask monitoreada con Seguridad Nacional")
    
    except ImportError as e:
        logger.error(f"Error importando Flask: {e}")
        raise ImportError("Flask no está instalado. Instala con: pip install flask")
    except Exception as e:
        logger.error(f"Error monitoreando aplicación Flask: {e}")
        raise


def _monitor_django(app, config_path: Optional[str] = None):
    """Monitorear aplicación Django"""
    try:
        import django
        from django.conf import settings as django_settings
        
        # Verificar que Django está configurado
        if not hasattr(django_settings, 'SECRET_KEY'):
            raise RuntimeError(
                "Django no está configurado correctamente. "
                "Asegúrate de que Django esté instalado y configurado."
            )
        
        # Obtener configuración
        from seguridad_nacional.config.settings import load_settings_from_file, get_settings
        if config_path:
            settings = load_settings_from_file(config_path)
        else:
            settings = get_settings()
        
        if not settings.enabled:
            logger.info("Seguridad Nacional deshabilitada")
            return
        
        # Para Django, el middleware se agrega en settings.py
        middleware_class = 'seguridad_nacional.middleware.django_middleware.DjangoSecurityMiddleware'
        
        if middleware_class not in django_settings.MIDDLEWARE:
            logger.warning(
                f"Middleware de Django no encontrado en MIDDLEWARE. "
                f"Agrega '{middleware_class}' a MIDDLEWARE en settings.py"
            )
        else:
            logger.info("Middleware de Django encontrado en configuración")
        
        # Agregar rutas del dashboard si está habilitado
        # Nota: Dashboard para Django aún no está implementado completamente
        if settings.dashboard_enabled:
            logger.warning(
                "Dashboard para Django aún no está completamente implementado. "
                "Usa FastAPI para acceso completo al dashboard."
            )
            # TODO: Implementar setup_django_dashboard_routes
        
        logger.info("Aplicación Django monitoreada con Seguridad Nacional")
    
    except ImportError as e:
        logger.error(f"Error importando Django: {e}")
        raise ImportError("Django no está instalado. Instala con: pip install django")
    except Exception as e:
        logger.error(f"Error monitoreando aplicación Django: {e}")
        raise


def protect(func: Optional[Callable] = None):
    """
    Decorador para proteger endpoints manualmente
    
    Uso:
        @protect
        @app.post("/api/data")
        async def receive_data(data: dict):
            return {"status": "ok"}
    """
    def decorator(f: Callable) -> Callable:
        # Por ahora, solo retornamos la función sin modificar
        # La protección se hace automáticamente con el middleware
        return f
    
    if func is None:
        return decorator
    else:
        return decorator(func)

