"""
Seguridad Nacional - Librería de Seguridad para Aplicaciones Python
Protección automatizada contra ciberataques para el contexto salvadoreño
"""

__version__ = "0.1.0"
__author__ = "Hackathon Team - Key Institute"

from seguridad_nacional.core.security_manager import SecurityManager
from seguridad_nacional.core.monitor import monitor, protect

__all__ = [
    "SecurityManager",
    "monitor",
    "protect",
]

