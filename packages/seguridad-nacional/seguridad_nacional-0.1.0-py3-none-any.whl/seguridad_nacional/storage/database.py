"""Base de datos SQLite para almacenar ataques y logs"""

import sqlite3
import aiosqlite
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Gestor de base de datos SQLite"""
    
    def __init__(self, db_path: str):
        """Inicializar la base de datos"""
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Asegurar que la base de datos existe y está inicializada"""
        # Crear directorio si no existe
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Crear tablas si no existen (usando conexión síncrona para inicialización)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de ataques
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                ip TEXT,
                country TEXT,
                threat_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocked INTEGER NOT NULL,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de IPs bloqueadas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocked_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL UNIQUE,
                blocked_at TEXT NOT NULL,
                blocked_until TEXT,
                severity TEXT NOT NULL,
                reason TEXT,
                attack_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de endpoints
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS endpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL UNIQUE,
                method TEXT NOT NULL,
                attack_count INTEGER DEFAULT 0,
                last_attack TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para mejor rendimiento
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attacks_timestamp ON attacks(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attacks_ip ON attacks(ip)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attacks_endpoint ON attacks(endpoint)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attacks_threat_type ON attacks(threat_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_blocked_ips_ip ON blocked_ips(ip)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_blocked_ips_blocked_until ON blocked_ips(blocked_until)")
        
        conn.commit()
        conn.close()
    
    async def connect(self):
        """Conectar a la base de datos"""
        if self.connection is None:
            self.connection = await aiosqlite.connect(self.db_path)
            self.connection.row_factory = aiosqlite.Row
    
    async def close(self):
        """Cerrar conexión a la base de datos"""
        if self.connection:
            await self.connection.close()
            self.connection = None
    
    async def save_attack(
        self,
        endpoint: str,
        method: str,
        ip: Optional[str],
        country: Optional[str],
        threat_type: str,
        severity: str,
        blocked: bool,
        details: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Guardar un ataque en la base de datos"""
        await self.connect()
        
        timestamp = datetime.now().isoformat()
        details_json = json.dumps(details) if details else None
        
        cursor = await self.connection.execute("""
            INSERT INTO attacks (timestamp, endpoint, method, ip, country, threat_type, severity, blocked, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, endpoint, method, ip, country, threat_type, severity, 1 if blocked else 0, details_json))
        
        await self.connection.commit()
        attack_id = cursor.lastrowid
        
        # Actualizar contador de ataques del endpoint
        await self.connection.execute("""
            INSERT OR REPLACE INTO endpoints (endpoint, method, attack_count, last_attack)
            VALUES (?, ?, COALESCE((SELECT attack_count FROM endpoints WHERE endpoint = ? AND method = ?), 0) + 1, ?)
        """, (endpoint, method, endpoint, method, timestamp))
        
        await self.connection.commit()
        
        return attack_id
    
    async def get_recent_attacks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtener ataques recientes"""
        await self.connect()
        
        cursor = await self.connection.execute("""
            SELECT * FROM attacks
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        attacks = []
        for row in rows:
            attacks.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "endpoint": row["endpoint"],
                "method": row["method"],
                "ip": row["ip"],
                "country": row["country"],
                "threat_type": row["threat_type"],
                "severity": row["severity"],
                "blocked": bool(row["blocked"]),
                "details": json.loads(row["details"]) if row["details"] else {},
            })
        
        return attacks
    
    async def get_top_endpoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener endpoints más vulnerables"""
        await self.connect()
        
        cursor = await self.connection.execute("""
            SELECT endpoint, method, attack_count, last_attack
            FROM endpoints
            ORDER BY attack_count DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        endpoints = []
        for row in rows:
            endpoints.append({
                "endpoint": row["endpoint"],
                "method": row["method"],
                "attack_count": row["attack_count"],
                "last_attack": row["last_attack"],
            })
        
        return endpoints
    
    async def get_top_attack_types(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtener tipos de ataques más frecuentes"""
        await self.connect()
        
        # Obtener todos los ataques con sus detalles
        cursor = await self.connection.execute("""
            SELECT threat_type, details, COUNT(*) as count
            FROM attacks
            GROUP BY threat_type
            ORDER BY count DESC
        """)
        
        rows = await cursor.fetchall()
        
        # Contar tipos de ataques desde los detalles (si hay múltiples tipos en un ataque)
        attack_type_counts = {}
        total_attacks = 0
        
        for row in rows:
            threat_type = row["threat_type"]
            count = row["count"]
            details = row["details"]
            
            # Contar el tipo principal
            if threat_type not in attack_type_counts:
                attack_type_counts[threat_type] = 0
            attack_type_counts[threat_type] += count
            total_attacks += count
            
            # Si hay múltiples tipos en los detalles, contarlos también
            if details:
                try:
                    details_dict = json.loads(details) if isinstance(details, str) else details
                    all_threat_types = details_dict.get("all_threat_types", [])
                    if all_threat_types and len(all_threat_types) > 1:
                        # Hay múltiples tipos, contar cada uno
                        for at_type in all_threat_types:
                            if at_type != threat_type:  # No contar el principal dos veces
                                if at_type not in attack_type_counts:
                                    attack_type_counts[at_type] = 0
                                attack_type_counts[at_type] += 1  # Contar como un ataque adicional
                                total_attacks += 1
                except Exception as e:
                    logger.debug(f"Error parseando detalles: {e}")
        
        # Ordenar por count y limitar
        sorted_types = sorted(attack_type_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        attack_types = []
        for threat_type, count in sorted_types:
            percentage = (count / total_attacks) * 100 if total_attacks > 0 else 0
            attack_types.append({
                "type": threat_type,
                "count": count,
                "percentage": round(percentage, 2),
            })
        
        return attack_types
    
    async def get_top_countries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener países con más ataques"""
        await self.connect()
        
        # Obtener países, incluyendo NULL como "Local" o "El Salvador"
        cursor = await self.connection.execute("""
            SELECT 
                CASE 
                    WHEN country IS NULL OR country = '' THEN 'El Salvador'
                    ELSE country
                END as country,
                COUNT(*) as count
            FROM attacks
            GROUP BY 
                CASE 
                    WHEN country IS NULL OR country = '' THEN 'El Salvador'
                    ELSE country
                END
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        countries = []
        for row in rows:
            countries.append({
                "country": row["country"] or "El Salvador",  # Por defecto El Salvador para localhost
                "count": row["count"],
            })
        
        return countries
    
    async def get_blocked_ips(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener IPs bloqueadas"""
        await self.connect()
        
        cursor = await self.connection.execute("""
            SELECT * FROM blocked_ips
            ORDER BY blocked_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        blocked_ips = []
        for row in rows:
            blocked_ips.append({
                "ip": row["ip"],
                "blocked_at": row["blocked_at"],
                "blocked_until": row["blocked_until"],
                "severity": row["severity"],
                "reason": row["reason"],
                "attack_count": row["attack_count"],
            })
        
        return blocked_ips
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas generales"""
        await self.connect()
        
        # Total de ataques
        cursor = await self.connection.execute("SELECT COUNT(*) as total FROM attacks")
        total_row = await cursor.fetchone()
        total_attacks = total_row["total"] if total_row else 0
        
        # Ataques de hoy
        today = datetime.now().date().isoformat()
        cursor = await self.connection.execute("""
            SELECT COUNT(*) as total FROM attacks
            WHERE DATE(timestamp) = ?
        """, (today,))
        today_row = await cursor.fetchone()
        attacks_today = today_row["total"] if today_row else 0
        
        # Ataques últimas 24 horas
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor = await self.connection.execute("""
            SELECT COUNT(*) as total FROM attacks
            WHERE timestamp >= ?
        """, (yesterday,))
        last24h_row = await cursor.fetchone()
        attacks_24h = last24h_row["total"] if last24h_row else 0
        
        # Ataques bloqueados
        cursor = await self.connection.execute("SELECT COUNT(*) as total FROM attacks WHERE blocked = 1")
        blocked_row = await cursor.fetchone()
        blocked_attacks = blocked_row["total"] if blocked_row else 0
        
        # Ataques permitidos
        allowed_attacks = total_attacks - blocked_attacks
        
        # Endpoints protegidos
        cursor = await self.connection.execute("SELECT COUNT(DISTINCT endpoint) as total FROM endpoints")
        endpoints_row = await cursor.fetchone()
        endpoints_protected = endpoints_row["total"] if endpoints_row else 0
        
        # Determinar estado del sistema
        status = "normal"
        if attacks_24h > 100:
            status = "critical"
        elif attacks_24h > 50:
            status = "alert"
        
        # Tasa de bloqueo
        block_rate = (blocked_attacks / total_attacks * 100) if total_attacks > 0 else 0
        
        return {
            "total_attacks": total_attacks,
            "attacks_today": attacks_today,
            "attacks_24h": attacks_24h,
            "blocked_attacks": blocked_attacks,
            "allowed_attacks": allowed_attacks,
            "block_rate": round(block_rate, 2),
            "endpoints_protected": endpoints_protected,
            "status": status,
        }
    
    async def get_attack_count_by_ip(self, ip: str) -> int:
        """Obtener número de ataques desde una IP"""
        await self.connect()
        cursor = await self.connection.execute("SELECT COUNT(*) as count FROM attacks WHERE ip = ?", (ip,))
        row = await cursor.fetchone()
        count = row["count"] if row else 0
        return count
    
    async def get_all_attacks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener todos los ataques (para exportar)"""
        await self.connect()
        
        query = "SELECT * FROM attacks ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor = await self.connection.execute(query)
        rows = await cursor.fetchall()
        
        attacks = []
        for row in rows:
            attacks.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "endpoint": row["endpoint"],
                "method": row["method"],
                "ip": row["ip"],
                "country": row["country"] or "El Salvador",
                "threat_type": row["threat_type"],
                "severity": row["severity"],
                "blocked": bool(row["blocked"]),
                "details": json.loads(row["details"]) if row["details"] else {},
            })
        
        return attacks
    
    async def get_attack_trends(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtener tendencias de ataques en el tiempo"""
        await self.connect()
        
        # Obtener ataques por hora
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor = await self.connection.execute("""
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as count,
                COUNT(CASE WHEN blocked = 1 THEN 1 END) as blocked_count
            FROM attacks
            WHERE timestamp >= ?
            GROUP BY strftime('%Y-%m-%d %H:00:00', timestamp)
            ORDER BY hour ASC
        """, (since,))
        
        rows = await cursor.fetchall()
        
        trends = []
        for row in rows:
            trends.append({
                "hour": row["hour"],
                "total": row["count"],
                "blocked": row["blocked_count"],
                "allowed": row["count"] - row["blocked_count"],
            })
        
        return trends
    
    def __del__(self):
        """Cerrar conexión al destruir"""
        # No podemos usar async en __del__
        # La conexión se cierra automáticamente cuando el objeto se destruye
        pass

