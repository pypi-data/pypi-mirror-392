"""Detector de comportamientos sospechosos"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

from seguridad_nacional.detectors.base import BaseDetector
from seguridad_nacional.storage.database import Database

logger = logging.getLogger(__name__)


class SuspiciousBehaviorDetector(BaseDetector):
    """Detector de comportamientos sospechosos"""
    
    def __init__(self, db: Database):
        """Inicializar el detector"""
        self.db = db
        self.request_counts = defaultdict(int)  # IP -> count
        self.request_timestamps = defaultdict(list)  # IP -> [timestamps]
        self.country_changes = defaultdict(set)  # IP -> {countries}
        
        # Umbrales
        self.REQUESTS_PER_MINUTE_THRESHOLD = 60
        self.COUNTRY_CHANGE_THRESHOLD = 3
        self.REQUESTS_IN_SHORT_TIME = 10  # 10 requests en menos de 1 minuto
    
    async def detect(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detectar comportamientos sospechosos"""
        ip = request_data.get("client_ip")
        if not ip:
            return {
                "is_threat": False,
                "threat_type": None,
                "severity": "none",
                "details": {},
            }
        
        threats = []
        current_time = datetime.now()
        
        # 1. Verificar tasa de requests por minuto
        threat = await self._check_request_rate(ip, current_time)
        if threat:
            threats.append(threat)
        
        # 2. Verificar cambios de país (se obtiene desde la base de datos)
        threat = await self._check_country_changes(ip)
        if threat:
            threats.append(threat)
        
        # 3. Verificar patrones de scraping
        threat = await self._check_scraping_patterns(request_data)
        if threat:
            threats.append(threat)
        
        # 4. Verificar headers anómalos
        threat = self._check_anomalous_headers(request_data)
        if threat:
            threats.append(threat)
        
        if threats:
            # Retornar la amenaza más severa
            return {
                "is_threat": True,
                "threat_type": "suspicious_behavior",
                "severity": "low",
                "details": {
                    "threats": threats,
                    "count": len(threats),
                },
            }
        
        return {
            "is_threat": False,
            "threat_type": None,
            "severity": "none",
            "details": {},
        }
    
    async def _check_request_rate(self, ip: str, current_time: datetime) -> Optional[Dict[str, Any]]:
        """Verificar tasa de requests por minuto"""
        # Limpiar timestamps antiguos (más de 1 minuto)
        one_minute_ago = current_time - timedelta(minutes=1)
        self.request_timestamps[ip] = [
            ts for ts in self.request_timestamps[ip] if ts > one_minute_ago
        ]
        
        # Agregar timestamp actual
        self.request_timestamps[ip].append(current_time)
        
        # Contar requests en el último minuto
        requests_last_minute = len(self.request_timestamps[ip])
        
        if requests_last_minute > self.REQUESTS_PER_MINUTE_THRESHOLD:
            return {
                "type": "high_request_rate",
                "requests_per_minute": requests_last_minute,
                "threshold": self.REQUESTS_PER_MINUTE_THRESHOLD,
            }
        
        return None
    
    async def _check_country_changes(self, ip: str) -> Optional[Dict[str, Any]]:
        """Verificar cambios de país en corto tiempo"""
        # Obtener historial de países desde la base de datos
        try:
            await self.db.connect()
            cursor = await self.db.connection.execute("""
                SELECT DISTINCT country FROM attacks
                WHERE ip = ? AND timestamp >= datetime('now', '-1 hour')
            """, (ip,))
            
            rows = await cursor.fetchall()
            countries_in_db = {row["country"] for row in rows if row["country"]}
            
            if len(countries_in_db) > self.COUNTRY_CHANGE_THRESHOLD:
                return {
                    "type": "country_change",
                    "countries": list(countries_in_db),
                    "count": len(countries_in_db),
                    "threshold": self.COUNTRY_CHANGE_THRESHOLD,
                }
        except Exception as e:
            logger.error(f"Error verificando cambios de país: {e}")
        
        return None
    
    async def _check_scraping_patterns(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Verificar patrones de scraping"""
        user_agent = request_data.get("user_agent", "")
        path = request_data.get("path", "")
        
        # Verificar user-agent de bots comunes
        bot_patterns = [
            "bot", "crawler", "spider", "scraper",
            "curl", "wget", "python-requests",
        ]
        
        user_agent_lower = user_agent.lower()
        for pattern in bot_patterns:
            if pattern in user_agent_lower:
                return {
                    "type": "scraping_pattern",
                    "user_agent": user_agent,
                    "pattern": pattern,
                }
        
        # Verificar múltiples requests a endpoints similares
        # (esto se detectaría mejor con historial, pero por ahora solo verificamos el patrón)
        if "/api/" in path and len(path.split("/")) > 4:
            # Endpoints muy anidados pueden ser intentos de scraping
            return {
                "type": "deep_path_scraping",
                "path": path,
            }
        
        return None
    
    def _check_anomalous_headers(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Verificar headers anómalos"""
        headers = request_data.get("headers", {})
        
        # Verificar ausencia de headers comunes
        common_headers = ["user-agent", "accept", "accept-language"]
        missing_headers = [h for h in common_headers if h.lower() not in [k.lower() for k in headers.keys()]]
        
        if len(missing_headers) >= 2:
            return {
                "type": "missing_headers",
                "missing": missing_headers,
            }
        
        # Verificar user-agent sospechoso
        user_agent = headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            return {
                "type": "suspicious_user_agent",
                "user_agent": user_agent,
            }
        
        return None

