"""Middleware para FastAPI"""

import asyncio
import logging
from typing import Callable, Optional, Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from seguridad_nacional.core.security_manager import get_manager
from seguridad_nacional.config.settings import get_settings

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de seguridad para FastAPI"""
    
    def __init__(self, app, config_path: Optional[str] = None):
        """Inicializar el middleware"""
        super().__init__(app)
        self.manager = get_manager(config_path)
        self.settings = get_settings()
        self.skip_paths = [
            "/seguridad",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico",
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Procesar request"""
        # Verificar si la ruta debe ser omitida
        if any(request.url.path.startswith(path) for path in self.skip_paths):
            return await call_next(request)
        
        # Verificar si está habilitado
        if not self.settings.enabled:
            return await call_next(request)
        
        # Obtener información del request
        client_ip = self._get_client_ip(request)
        method = request.method
        path = request.url.path
        headers = dict(request.headers)
        user_agent = headers.get("user-agent")
        
        # Obtener parámetros
        params = dict(request.query_params)
        
        # NO leer el body aquí - esto consume el stream
        # En su lugar, analizamos solo parámetros y headers para GET
        # Para POST/PUT/PATCH, el análisis se hace después de que FastAPI procese el request
        body = None
        
        # Solo analizar body para métodos POST/PUT/PATCH si es necesario
        # Pero NO leerlo aquí para evitar consumir el stream
        # El análisis se puede hacer después o solo con parámetros/headers
        
        # Analizar request
        try:
            if self.settings.async_analysis:
                # Análisis asíncrono (no bloquea el request, pero lo analiza)
                # Ejecutar análisis en segundo plano sin esperar
                asyncio.create_task(
                    self._analyze_request_async(
                        method=method,
                        path=path,
                        headers=headers,
                        body=body,
                        params=params,
                        client_ip=client_ip,
                        user_agent=user_agent,
                    )
                )
                
                # Responder inmediatamente (sin esperar análisis)
                return await call_next(request)
            else:
                # Análisis síncrono (bloquea hasta analizar)
                analysis_result = await self.manager.analyze_request(
                    method=method,
                    path=path,
                    headers=headers,
                    body=body,
                    params=params,
                    client_ip=client_ip,
                    user_agent=user_agent,
                )
                
                # Si es una amenaza y debe bloquearse, bloquear
                if analysis_result.get("is_threat") and analysis_result.get("blocked"):
                    threat_type = analysis_result.get("threat_type", "unknown")
                    severity = analysis_result.get("severity", "medium")
                    
                    return JSONResponse(
                        status_code=403,
                        content={
                            "error": "Request bloqueado por seguridad",
                            "threat_type": threat_type,
                            "severity": severity,
                            "message": "Tu request fue bloqueado por detectar actividad sospechosa.",
                        },
                    )
                
                # Continuar con el request normal
                return await call_next(request)
        
        except Exception as e:
            logger.error(f"Error en middleware de seguridad: {e}")
            # En caso de error, permitir el request (fail-open)
            return await call_next(request)
    
    async def _analyze_request_async(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[str],
        params: Dict[str, Any],
        client_ip: Optional[str],
        user_agent: Optional[str],
    ):
        """Analizar request de forma asíncrona (sin bloquear)"""
        try:
            analysis_result = await self.manager.analyze_request(
                method=method,
                path=path,
                headers=headers,
                body=body,
                params=params,
                client_ip=client_ip,
                user_agent=user_agent,
            )
            
            # Si es una amenaza, loguear
            if analysis_result.get("is_threat"):
                threat_type = analysis_result.get("threat_type", "unknown")
                severity = analysis_result.get("severity", "low")
                blocked = analysis_result.get("blocked", False)
                status = "BLOQUEADO" if blocked else "REGISTRADO"
                logger.warning(
                    f"Ataque detectado [{status}]: {client_ip} - {path} - {threat_type} - {severity}"
                )
        except Exception as e:
            logger.error(f"Error en análisis asíncrono: {e}")
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Obtener IP del cliente"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Tomar la primera IP de la cadena
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # IP directa
        if request.client:
            return request.client.host
        
        return None

