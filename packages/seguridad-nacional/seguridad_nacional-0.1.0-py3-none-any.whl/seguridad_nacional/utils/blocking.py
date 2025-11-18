"""Sistema de bloqueo de IPs"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import aiosqlite

from seguridad_nacional.config.settings import Settings
from seguridad_nacional.storage.database import Database

logger = logging.getLogger(__name__)


class IPBlocker:
    """Gestor de bloqueo de IPs"""
    
    def __init__(self, db: Database, settings: Settings):
        """Inicializar el bloqueador de IPs"""
        self.db = db
        self.settings = settings
    
    async def is_blocked(self, ip: str) -> bool:
        """Verificar si una IP está bloqueada"""
        await self.db.connect()
        
        cursor = await self.db.connection.execute("""
            SELECT blocked_until FROM blocked_ips
            WHERE ip = ?
        """, (ip,))
        
        row = await cursor.fetchone()
        
        if row is None:
            return False
        
        blocked_until = row["blocked_until"]
        
        # Si no hay fecha de expiración, está bloqueada indefinidamente
        if blocked_until is None:
            return True
        
        # Verificar si el bloqueo ha expirado
        try:
            blocked_until_dt = datetime.fromisoformat(blocked_until)
            if datetime.now() > blocked_until_dt:
                # Bloqueo expirado, eliminar de la lista
                await self.db.connection.execute("DELETE FROM blocked_ips WHERE ip = ?", (ip,))
                await self.db.connection.commit()
                return False
            return True
        except Exception as e:
            logger.error(f"Error verificando bloqueo de IP {ip}: {e}")
            return True
    
    async def block_ip(
        self,
        ip: str,
        severity: str,
        reason: Optional[str] = None,
    ):
        """Bloquear una IP"""
        await self.db.connect()
        
        # Determinar duración del bloqueo según severidad
        blocked_until = None
        if severity == "critical":
            # Bloqueo indefinido
            blocked_until = None
        elif severity == "high":
            # Bloqueo de 1 hora
            blocked_until = (datetime.now() + timedelta(hours=1)).isoformat()
        elif severity == "medium":
            # Bloqueo de 30 minutos
            blocked_until = (datetime.now() + timedelta(minutes=30)).isoformat()
        else:  # low
            # Bloqueo de 30 minutos
            blocked_until = (datetime.now() + timedelta(minutes=30)).isoformat()
        
        # Obtener contador de ataques
        attack_count = await self.db.get_attack_count_by_ip(ip)
        
        # Insertar o actualizar bloqueo
        try:
            await self.db.connection.execute("""
                INSERT OR REPLACE INTO blocked_ips (ip, blocked_at, blocked_until, severity, reason, attack_count)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ip, datetime.now().isoformat(), blocked_until, severity, reason, attack_count))
            
            await self.db.connection.commit()
            logger.info(f"IP {ip} bloqueada - Severidad: {severity}, Razón: {reason}")
        except Exception as e:
            logger.error(f"Error bloqueando IP {ip}: {e}")
            await self.db.connection.rollback()
    
    async def unblock_ip(self, ip: str):
        """Desbloquear una IP"""
        await self.db.connect()
        await self.db.connection.execute("DELETE FROM blocked_ips WHERE ip = ?", (ip,))
        await self.db.connection.commit()
        logger.info(f"IP {ip} desbloqueada")

