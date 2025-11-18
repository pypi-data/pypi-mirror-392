"""Clase base para detectores"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseDetector(ABC):
    """Clase base para detectores de vulnerabilidades"""
    
    @abstractmethod
    async def detect(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detectar amenazas en un request
        
        Args:
            request_data: Datos del request a analizar
        
        Returns:
            Dict con información de la detección:
            - is_threat: bool - Si es una amenaza
            - threat_type: str - Tipo de amenaza
            - severity: str - Severidad (low, medium, high, critical)
            - details: Dict - Detalles adicionales
        """
        pass
    
    def _get_severity(self, threat_type: str, confidence: float = 1.0) -> str:
        """Determinar severidad basada en el tipo de amenaza"""
        severity_map = {
            "sql_injection": "high",
            "xss": "medium",
            "command_injection": "critical",
            "path_traversal": "high",
            "suspicious_behavior": "low",
            "dos": "medium",
            "phishing": "low",
            "ransomware": "critical",
        }
        
        base_severity = severity_map.get(threat_type, "low")
        
        # Ajustar según confianza
        if confidence < 0.5:
            if base_severity == "critical":
                return "high"
            elif base_severity == "high":
                return "medium"
            elif base_severity == "medium":
                return "low"
        
        return base_severity

