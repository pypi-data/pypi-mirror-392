"""Middleware para Django"""

import asyncio
import logging
from typing import Optional, Dict, Any
from django.http import JsonResponse, HttpRequest
from django.utils.deprecation import MiddlewareMixin

from seguridad_nacional.core.security_manager import get_manager
from seguridad_nacional.config.settings import get_settings

logger = logging.getLogger(__name__)


class DjangoSecurityMiddleware(MiddlewareMixin):
    """Middleware de seguridad para Django"""
    
    def __init__(self, get_response, config_path: Optional[str] = None):
        """Inicializar el middleware"""
        super().__init__(get_response)
        self.manager = get_manager(config_path)
        self.settings = get_settings()
        self.config_path = config_path
        self.skip_paths = [
            "/seguridad",
            "/static",
            "/media",
            "/favicon.ico",
            "/admin",
        ]
        
        logger.info("DjangoSecurityMiddleware inicializado")
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Obtener IP del cliente"""
        # Intentar obtener IP real (detrás de proxy)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        elif request.META.get('HTTP_X_REAL_IP'):
            return request.META.get('HTTP_X_REAL_IP')
        else:
            return request.META.get('REMOTE_ADDR', 'unknown')
    
    def process_request(self, request: HttpRequest):
        """Procesar request antes de que llegue a la vista"""
        # Verificar si la ruta debe ser omitida
        if any(request.path.startswith(path) for path in self.skip_paths):
            return None
        
        # Verificar si está habilitado
        if not self.settings.enabled:
            return None
        
        try:
            # Obtener información del request
            client_ip = self._get_client_ip(request)
            method = request.method
            path = request.path
            headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Obtener parámetros
            params = dict(request.GET)
            
            # Obtener body
            body = None
            if request.body:
                try:
                    body = request.body.decode('utf-8')
                except:
                    body = str(request.body)
            
            # Analizar request
            if self.settings.async_analysis:
                # Análisis asíncrono (no bloquea)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self.manager.analyze_request(
                            method=method,
                            path=path,
                            headers=headers,
                            body=body,
                            params=params,
                            client_ip=client_ip,
                            user_agent=user_agent,
                        )
                    )
                finally:
                    loop.close()
            else:
                # Análisis síncrono (bloquea hasta completar)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self.manager.analyze_request(
                            method=method,
                            path=path,
                            headers=headers,
                            body=body,
                            params=params,
                            client_ip=client_ip,
                            user_agent=user_agent,
                        )
                    )
                finally:
                    loop.close()
            
            # Solo procesar resultado si no es análisis asíncrono
            if not self.settings.async_analysis and result:
                # Si es una amenaza y debe bloquearse
                if result.get("is_threat") and result.get("blocked"):
                    logger.warning(
                        f"Request bloqueado: {method} {path} desde {client_ip} - "
                        f"Tipo: {result.get('threat_type')}"
                    )
                    
                    # Retornar respuesta de bloqueo
                    return JsonResponse({
                        "error": "Acceso denegado",
                        "message": "Tu solicitud ha sido bloqueada por razones de seguridad",
                        "threat_type": result.get("threat_type"),
                    }, status=403)
                
                # Si es amenaza pero no se bloquea, solo registrar
                if result.get("is_threat"):
                    logger.info(
                        f"Amenaza detectada (no bloqueada): {method} {path} desde {client_ip} - "
                        f"Tipo: {result.get('threat_type')}"
                    )
            
            # Continuar con el request normal
            return None
            
        except Exception as e:
            logger.error(f"Error en middleware de seguridad Django: {e}")
            # En caso de error, permitir que el request continúe
            return None

