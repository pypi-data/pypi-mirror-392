"""Gestor principal de seguridad"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from seguridad_nacional.config.settings import get_settings, Settings
from seguridad_nacional.storage.database import Database
from seguridad_nacional.detectors.sql_injection import SQLInjectionDetector
from seguridad_nacional.detectors.xss import XSSDetector
from seguridad_nacional.detectors.suspicious_behavior import SuspiciousBehaviorDetector
from seguridad_nacional.utils.blocking import IPBlocker
from seguridad_nacional.utils.geolocation import GeolocationService

logger = logging.getLogger(__name__)


class SecurityManager:
    """Gestor principal de seguridad"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Inicializar el gestor de seguridad"""
        from seguridad_nacional.config.settings import load_settings_from_file
        
        # Cargar configuración
        if config_path:
            self.settings = load_settings_from_file(config_path)
        else:
            self.settings = get_settings()
        
        # Inicializar componentes
        self.db = Database(self.settings.db_path)
        self.ip_blocker = IPBlocker(self.db, self.settings)
        self.geolocation = GeolocationService(self.settings) if self.settings.geolocation_enabled else None
        
        # Inicializar detectores
        self.detectors = []
        if self.settings.sql_injection_enabled:
            self.detectors.append(SQLInjectionDetector())
        if self.settings.xss_enabled:
            self.detectors.append(XSSDetector())
        if self.settings.suspicious_behavior_enabled:
            self.detectors.append(SuspiciousBehaviorDetector(self.db))
        
        # Configurar logging
        logging.basicConfig(
            level=getattr(logging, self.settings.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=self.settings.log_file
        )
        
        logger.info("SecurityManager inicializado")
    
    async def analyze_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analizar un request para detectar amenazas
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            path: Ruta del endpoint
            headers: Headers HTTP
            body: Cuerpo del request (opcional)
            params: Parámetros del request (opcional)
            client_ip: IP del cliente
            user_agent: User-Agent del cliente
        
        Returns:
            Dict con información del análisis:
            - is_threat: bool - Si es una amenaza
            - threat_type: str - Tipo de amenaza detectada
            - severity: str - Severidad (low, medium, high, critical)
            - blocked: bool - Si fue bloqueado
            - details: Dict - Detalles adicionales
        """
        if not self.settings.enabled:
            return {
                "is_threat": False,
                "threat_type": None,
                "severity": "none",
                "blocked": False,
                "details": {},
            }
        
        # Verificar whitelist
        if client_ip and client_ip in self.settings.whitelist_ips:
            return {
                "is_threat": False,
                "threat_type": "whitelist",
                "severity": "none",
                "blocked": False,
                "details": {"reason": "IP en whitelist"},
            }
        
        # Preparar datos para análisis
        request_data = {
            "method": method,
            "path": path,
            "headers": headers,
            "body": body or "",
            "params": params or {},
            "client_ip": client_ip,
            "user_agent": user_agent,
        }
        
        # Verificar si la IP está bloqueada (pero seguir analizando para registrar)
        ip_blocked = False
        if client_ip and await self.ip_blocker.is_blocked(client_ip):
            ip_blocked = True
            # NO retornar aquí - continuar analizando para detectar el tipo de ataque
        
        # Analizar con todos los detectores
        threats = []
        for detector in self.detectors:
            try:
                result = await detector.detect(request_data)
                if result.get("is_threat", False):
                    threats.append(result)
            except Exception as e:
                logger.error(f"Error en detector {detector.__class__.__name__}: {e}")
        
        # Obtener geolocalización (una sola vez para todos los ataques)
        country = None
        if client_ip and self.geolocation:
            try:
                geo_data = await self.geolocation.get_location(client_ip)
                country = geo_data.get("country")
                # Si es localhost y devuelve "Local", usar "El Salvador" para el mapa
                if country == "Local":
                    country = "El Salvador"
                # Si no tiene país y es localhost, usar "El Salvador"
                if not country and client_ip in ["127.0.0.1", "localhost", "::1"]:
                    country = "El Salvador"
            except Exception as e:
                logger.error(f"Error obteniendo geolocalización: {e}")
                # Si falla y es localhost, usar "El Salvador"
                if client_ip in ["127.0.0.1", "localhost", "::1"]:
                    country = "El Salvador"
        
        # Si hay amenazas, guardar TODOS los tipos de ataques detectados
        if threats:
            # Ordenar por severidad para determinar cuál bloquear
            severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            threats.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 0), reverse=True)
            main_threat = threats[0]
            
            # Obtener todos los tipos de amenazas detectadas
            threat_types = [t.get("threat_type", "unknown") for t in threats]
            
            # Verificar whitelist de patrones
            threat_type = main_threat.get("threat_type", "unknown")
            if threat_type in self.settings.whitelist_patterns:
                return {
                    "is_threat": False,
                    "threat_type": "whitelist_pattern",
                    "severity": "none",
                    "blocked": False,
                    "details": {"reason": "Patrón en whitelist"},
                }
            
            # Determinar si bloquear (si la IP no estaba bloqueada previamente)
            severity = main_threat.get("severity", "low")
            should_block = ip_blocked or await self._should_block(severity, client_ip)
            
            # Guardar TODOS los tipos de ataques detectados
            # Si hay múltiples tipos, guardar registros separados para cada tipo
            attack_details = main_threat.get("details", {})
            attack_details["all_threat_types"] = threat_types
            attack_details["threat_count"] = len(threats)
            
            # Guardar el ataque principal (más severo)
            attack_id = await self.db.save_attack(
                endpoint=path,
                method=method,
                ip=client_ip,
                country=country or "El Salvador",  # Por defecto El Salvador para localhost
                threat_type=threat_type,  # Tipo principal (más severo)
                severity=severity,
                blocked=should_block,
                details=attack_details,
            )
            
            # Si hay múltiples tipos de ataques, guardar registros adicionales para cada tipo
            # Esto permite que aparezcan todos los tipos en las estadísticas
            for threat in threats[1:]:  # Empezar desde el segundo (el primero ya se guardó)
                additional_threat_type = threat.get("threat_type", "unknown")
                additional_severity = threat.get("severity", "low")
                
                # Guardar cada tipo de ataque adicional
                await self.db.save_attack(
                    endpoint=path,
                    method=method,
                    ip=client_ip,
                    country=country or "El Salvador",
                    threat_type=additional_threat_type,
                    severity=additional_severity,
                    blocked=should_block,  # Usar el mismo bloqueo
                    details=threat.get("details", {}),
                )
            
            # Bloquear IP si es necesario (solo si no estaba bloqueada previamente)
            if should_block and client_ip and not ip_blocked:
                await self.ip_blocker.block_ip(
                    ip=client_ip,
                    severity=severity,
                    reason=threat_type,
                )
            
            # Log de todos los tipos detectados
            if len(threat_types) > 1:
                logger.info(f"Múltiples tipos de ataques detectados: {', '.join(threat_types)} - Guardando como: {threat_type}")
            
            return {
                "is_threat": True,
                "threat_type": threat_type,  # Tipo principal
                "all_threat_types": threat_types,  # Todos los tipos detectados
                "severity": severity,
                "blocked": should_block,
                "details": attack_details,
                "attack_id": attack_id,
                "country": country,
            }
        
        # Si la IP está bloqueada pero no se detectó amenaza en este request, aún así bloquear
        if ip_blocked:
            # Guardar intento desde IP bloqueada
            country = None
            if client_ip and self.geolocation:
                try:
                    geo_data = await self.geolocation.get_location(client_ip)
                    country = geo_data.get("country")
                    # Si es localhost y no tiene país, usar "El Salvador"
                    if not country and client_ip in ["127.0.0.1", "localhost", "::1"]:
                        country = "El Salvador"
                except Exception as e:
                    logger.error(f"Error obteniendo geolocalización: {e}")
                    # Si falla y es localhost, usar "El Salvador"
                    if client_ip in ["127.0.0.1", "localhost", "::1"]:
                        country = "El Salvador"
            
            # Guardar como intento desde IP bloqueada
            attack_id = await self.db.save_attack(
                endpoint=path,
                method=method,
                ip=client_ip,
                country=country or "El Salvador",  # Por defecto El Salvador para localhost
                threat_type="blocked_ip",
                severity="high",
                blocked=True,
                details={"reason": "Intento desde IP bloqueada"},
            )
            
            return {
                "is_threat": True,
                "threat_type": "blocked_ip",
                "severity": "high",
                "blocked": True,
                "details": {"reason": "IP bloqueada"},
                "attack_id": attack_id,
                "country": country or "El Salvador",
            }
        
        return {
            "is_threat": False,
            "threat_type": None,
            "severity": "none",
            "blocked": False,
            "details": {},
        }
    
    async def _should_block(self, severity: str, client_ip: Optional[str] = None) -> bool:
        """Determinar si se debe bloquear basado en la severidad"""
        if not client_ip:
            return False
        
        # Verificar número de intentos desde esta IP
        attack_count = await self.db.get_attack_count_by_ip(client_ip)
        
        # Bloquear según severidad (más agresivo para hackathon)
        if severity == "critical":
            return True  # Bloquear inmediatamente
        elif severity == "high":
            return attack_count >= 1  # Bloquear después del primer ataque
        elif severity == "medium":
            return attack_count >= 3  # Bloquear después de 3 ataques
        else:  # low
            # Bloquear si supera el umbral configurado
            return attack_count >= self.settings.block_threshold
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas generales"""
        return await self.db.get_stats()
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtener datos para el dashboard"""
        stats = await self.get_stats()
        
        # Obtener datos adicionales
        recent_attacks = await self.db.get_recent_attacks(limit=20)
        top_endpoints = await self.db.get_top_endpoints(limit=10)
        top_attack_types = await self.db.get_top_attack_types(limit=5)
        top_countries = await self.db.get_top_countries(limit=10)
        blocked_ips = await self.db.get_blocked_ips(limit=10)
        
        # Obtener tendencias temporales (últimas 24 horas)
        trends = await self.db.get_attack_trends(hours=24)
        
        return {
            "general": stats,
            "recent_attacks": recent_attacks,
            "top_endpoints": top_endpoints,
            "top_attack_types": top_attack_types,
            "top_countries": top_countries,
            "blocked_ips": blocked_ips,
            "trends": trends,
        }
    
    def __del__(self):
        """Cerrar conexiones al destruir"""
        # No podemos usar async en __del__
        # La conexión se cierra automáticamente cuando el objeto se destruye
        pass


# Instancia global del gestor
_global_manager: Optional[SecurityManager] = None


def get_manager(config_path: Optional[str] = None) -> SecurityManager:
    """Obtener la instancia global del gestor"""
    global _global_manager
    if _global_manager is None:
        _global_manager = SecurityManager(config_path)
    return _global_manager


def set_manager(manager: SecurityManager):
    """Establecer la instancia global del gestor"""
    global _global_manager
    _global_manager = manager

