"""Middleware para Flask"""

import asyncio
import logging
from typing import Optional, Dict, Any
from flask import Flask, request, jsonify

from seguridad_nacional.core.security_manager import get_manager
from seguridad_nacional.config.settings import get_settings

logger = logging.getLogger(__name__)


class FlaskSecurityMiddleware:
    """Middleware de seguridad para Flask"""
    
    def __init__(self, app: Flask, config_path: Optional[str] = None):
        """Inicializar el middleware"""
        self.app = app
        self.manager = get_manager(config_path)
        self.settings = get_settings()
        self.skip_paths = [
            "/seguridad",
            "/static",
            "/favicon.ico",
        ]
        
        # Registrar el before_request handler
        self.app.before_request(self.analyze_request)
        
        logger.info("FlaskSecurityMiddleware inicializado")
    
    def _get_client_ip(self, request) -> str:
        """Obtener IP del cliente"""
        # Intentar obtener IP real (detrás de proxy)
        if request.headers.get("X-Forwarded-For"):
            return request.headers.get("X-Forwarded-For").split(",")[0].strip()
        elif request.headers.get("X-Real-IP"):
            return request.headers.get("X-Real-IP")
        else:
            return request.remote_addr or "unknown"
    
    def analyze_request(self):
        """Analizar request antes de que llegue a la ruta"""
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
            headers = dict(request.headers)
            user_agent = headers.get("User-Agent", "")
            
            # Obtener parámetros
            params = dict(request.args)
            
            # Obtener body
            body = None
            if request.is_json:
                body = str(request.get_json())
            elif request.data:
                try:
                    body = request.data.decode('utf-8')
                except:
                    body = str(request.data)
            
            # Analizar request (síncrono para Flask)
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
                    return jsonify({
                        "error": "Acceso denegado",
                        "message": "Tu solicitud ha sido bloqueada por razones de seguridad",
                        "threat_type": result.get("threat_type"),
                    }), 403
                
                # Si es amenaza pero no se bloquea, solo registrar
                if result.get("is_threat"):
                    logger.info(
                        f"Amenaza detectada (no bloqueada): {method} {path} desde {client_ip} - "
                        f"Tipo: {result.get('threat_type')}"
                    )
            
            # Continuar con el request normal
            return None
            
        except Exception as e:
            logger.error(f"Error en middleware de seguridad Flask: {e}")
            # En caso de error, permitir que el request continúe
            return None

