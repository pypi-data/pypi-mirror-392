"""Detector de SQL Injection"""

import re
import urllib.parse
from typing import Dict, Any, List, Optional

from seguridad_nacional.detectors.base import BaseDetector


class SQLInjectionDetector(BaseDetector):
    """Detector de inyección SQL"""
    
    # Patrones comunes de SQL Injection
    SQL_PATTERNS = [
        # Uniones
        r"(?i)(union\s+select)",
        r"(?i)(union\s+all\s+select)",
        
        # Comentarios SQL
        r"(?i)(--|#|\/\*)",
        r"(?i)(\/\*.*\*\/)",
        
        # Operadores lógicos
        r"(?i)(or\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+)",
        r"(?i)(or\s+['\"]?1['\"]?\s*=\s*['\"]?1)",
        r"(?i)(or\s+['\"]?['\"]?\s*=\s*['\"]?['\"])",
        
        # Funciones SQL
        r"(?i)(select\s+.+\s+from)",
        r"(?i)(insert\s+into)",
        r"(?i)(update\s+.+\s+set)",
        r"(?i)(delete\s+from)",
        r"(?i)(drop\s+table)",
        r"(?i)(drop\s+database)",
        r"(?i)(truncate\s+table)",
        
        # Funciones peligrosas
        r"(?i)(exec\s*\()",
        r"(?i)(execute\s*\()",
        r"(?i)(xp_cmdshell)",
        r"(?i)(sp_executesql)",
        
        # Tipos de datos
        r"(?i)(cast\s*\()",
        r"(?i)(convert\s*\()",
        r"(?i)(char\s*\()",
        
        # Time-based
        r"(?i)(sleep\s*\()",
        r"(?i)(waitfor\s+delay)",
        r"(?i)(benchmark\s*\()",
        
        # Boolean-based
        r"(?i)(and\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+)",
        r"(?i)(and\s+['\"]?1['\"]?\s*=\s*['\"]?1)",
        
        # Error-based
        r"(?i)(extractvalue\s*\()",
        r"(?i)(updatexml\s*\()",
        r"(?i)(exp\s*\()",
    ]
    
    def __init__(self):
        """Inicializar el detector"""
        self.patterns = [re.compile(pattern) for pattern in self.SQL_PATTERNS]
    
    async def detect(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detectar inyección SQL"""
        threats = []
        
        # Analizar parámetros
        params = request_data.get("params", {})
        for key, value in params.items():
            if isinstance(value, str):
                threat = self._check_value(value, f"param:{key}")
                if threat:
                    threats.append(threat)
        
        # Analizar body
        body = request_data.get("body", "")
        if body:
            if isinstance(body, str):
                threat = self._check_value(body, "body")
                if threat:
                    threats.append(threat)
            elif isinstance(body, dict):
                for key, value in body.items():
                    if isinstance(value, str):
                        threat = self._check_value(value, f"body:{key}")
                        if threat:
                            threats.append(threat)
        
        # Analizar headers (algunos ataques pueden estar en headers)
        headers = request_data.get("headers", {})
        for key, value in headers.items():
            if isinstance(value, str):
                # Decodificar URL encoding
                try:
                    decoded = urllib.parse.unquote(value)
                    threat = self._check_value(decoded, f"header:{key}")
                    if threat:
                        threats.append(threat)
                except Exception:
                    pass
        
        if threats:
            # Retornar la amenaza más severa
            return {
                "is_threat": True,
                "threat_type": "sql_injection",
                "severity": "high",
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
    
    def _check_value(self, value: str, source: str) -> Optional[Dict[str, Any]]:
        """Verificar si un valor contiene patrones de SQL Injection"""
        if not value:
            return None
        
        # Decodificar URL encoding
        try:
            decoded = urllib.parse.unquote(value)
        except Exception:
            decoded = value
        
        # Verificar patrones
        for pattern in self.patterns:
            if pattern.search(decoded):
                return {
                    "source": source,
                    "pattern": pattern.pattern,
                    "value": decoded[:100],  # Limitar longitud
                }
        
        return None

