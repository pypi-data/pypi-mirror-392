"""Detector de XSS (Cross-Site Scripting)"""

import re
import urllib.parse
import html
from typing import Dict, Any, Optional

from seguridad_nacional.detectors.base import BaseDetector


class XSSDetector(BaseDetector):
    """Detector de XSS"""
    
    # Patrones comunes de XSS
    XSS_PATTERNS = [
        # Script tags
        r"(?i)<script[^>]*>.*?</script>",
        r"(?i)<script",
        
        # Event handlers
        r"(?i)on\w+\s*=",
        r"(?i)(onclick|onerror|onload|onmouseover)",
        
        # JavaScript URLs
        r"(?i)javascript:",
        r"(?i)vbscript:",
        r"(?i)data:text/html",
        
        # Iframes
        r"(?i)<iframe[^>]*>",
        r"(?i)<frame[^>]*>",
        
        # Object/Embed
        r"(?i)<object[^>]*>",
        r"(?i)<embed[^>]*>",
        
        # Img con onerror
        r"(?i)<img[^>]*onerror",
        r"(?i)<img[^>]*src\s*=\s*['\"]?javascript:",
        
        # SVG
        r"(?i)<svg[^>]*onload",
        
        # Expressions
        r"(?i)expression\s*\(",
        
        # Encodings comunes
        r"(?i)%3Cscript",
        r"(?i)%3C%2Fscript",
        r"(?i)&lt;script",
        r"(?i)&lt;%2Fscript",
        
        # Base64
        r"(?i)data:image/svg\+xml;base64",
    ]
    
    def __init__(self):
        """Inicializar el detector"""
        self.patterns = [re.compile(pattern) for pattern in self.XSS_PATTERNS]
    
    async def detect(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detectar XSS"""
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
        
        # Analizar headers
        headers = request_data.get("headers", {})
        for key, value in headers.items():
            if isinstance(value, str):
                # Decodificar URL encoding y HTML entities
                try:
                    decoded = urllib.parse.unquote(value)
                    decoded = html.unescape(decoded)
                    threat = self._check_value(decoded, f"header:{key}")
                    if threat:
                        threats.append(threat)
                except Exception:
                    pass
        
        if threats:
            return {
                "is_threat": True,
                "threat_type": "xss",
                "severity": "medium",
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
        """Verificar si un valor contiene patrones de XSS"""
        if not value:
            return None
        
        # Decodificar URL encoding
        try:
            decoded = urllib.parse.unquote(value)
        except Exception:
            decoded = value
        
        # Decodificar HTML entities
        try:
            decoded = html.unescape(decoded)
        except Exception:
            pass
        
        # Verificar patrones
        for pattern in self.patterns:
            if pattern.search(decoded):
                return {
                    "source": source,
                    "pattern": pattern.pattern,
                    "value": decoded[:100],  # Limitar longitud
                }
        
        return None

