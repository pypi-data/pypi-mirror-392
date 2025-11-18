"""Rutas del dashboard"""

import logging
import csv
import io
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

from seguridad_nacional.core.security_manager import SecurityManager
from seguridad_nacional.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials, settings: Settings) -> bool:
    """Verificar credenciales del dashboard"""
    return (
        credentials.username == settings.dashboard_user and
        credentials.password == settings.dashboard_password
    )


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    settings: Settings = Depends(get_settings),
) -> str:
    """Obtener usuario actual (autenticación)"""
    if not verify_credentials(credentials, settings):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def setup_dashboard_routes(app: FastAPI, manager: SecurityManager, settings: Settings):
    """Configurar rutas del dashboard"""
    dashboard_path = settings.dashboard_path
    
    @app.get(f"{dashboard_path}/dashboard", response_class=HTMLResponse)
    async def dashboard(user: str = Depends(get_current_user)):
        """Dashboard principal"""
        from seguridad_nacional.dashboard.templates import get_dashboard_html
        return HTMLResponse(content=get_dashboard_html())
    
    @app.get(f"{dashboard_path}/api/stats")
    async def get_stats(user: str = Depends(get_current_user)):
        """Obtener estadísticas generales"""
        try:
            stats = await manager.get_stats()
            return JSONResponse(content=stats)
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get(f"{dashboard_path}/api/map")
    async def get_map_data(user: str = Depends(get_current_user)):
        """Obtener datos para el mapa"""
        try:
            dashboard_data = await manager.get_dashboard_data()
            countries = dashboard_data.get("top_countries", [])
            
            # Formatear datos para el mapa
            map_data = {
                "countries": countries,
                "total_countries": len(countries),
            }
            
            return JSONResponse(content=map_data)
        except Exception as e:
            logger.error(f"Error obteniendo datos del mapa: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get(f"{dashboard_path}/api/endpoints")
    async def get_endpoints(user: str = Depends(get_current_user)):
        """Obtener endpoints más vulnerables"""
        try:
            dashboard_data = await manager.get_dashboard_data()
            endpoints = dashboard_data.get("top_endpoints", [])
            return JSONResponse(content={"endpoints": endpoints})
        except Exception as e:
            logger.error(f"Error obteniendo endpoints: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get(f"{dashboard_path}/api/attacks")
    async def get_attack_types(user: str = Depends(get_current_user)):
        """Obtener tipos de ataques"""
        try:
            dashboard_data = await manager.get_dashboard_data()
            attack_types = dashboard_data.get("top_attack_types", [])
            return JSONResponse(content={"attack_types": attack_types})
        except Exception as e:
            logger.error(f"Error obteniendo tipos de ataques: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get(f"{dashboard_path}/api/recent")
    async def get_recent_attacks(
        user: str = Depends(get_current_user),
        limit: int = 20,
    ):
        """Obtener ataques recientes"""
        try:
            dashboard_data = await manager.get_dashboard_data()
            recent_attacks = dashboard_data.get("recent_attacks", [])[:limit]
            return JSONResponse(content={"attacks": recent_attacks})
        except Exception as e:
            logger.error(f"Error obteniendo ataques recientes: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get(f"{dashboard_path}/api/ips")
    async def get_blocked_ips(user: str = Depends(get_current_user)):
        """Obtener IPs bloqueadas"""
        try:
            dashboard_data = await manager.get_dashboard_data()
            blocked_ips = dashboard_data.get("blocked_ips", [])
            return JSONResponse(content={"blocked_ips": blocked_ips})
        except Exception as e:
            logger.error(f"Error obteniendo IPs bloqueadas: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get(f"{dashboard_path}/api/dashboard")
    async def get_dashboard_data(user: str = Depends(get_current_user)):
        """Obtener todos los datos del dashboard"""
        try:
            dashboard_data = await manager.get_dashboard_data()
            return JSONResponse(content=dashboard_data)
        except Exception as e:
            logger.error(f"Error obteniendo datos del dashboard: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post(f"{dashboard_path}/api/unblock/{{ip}}")
    async def unblock_ip(
        ip: str,
        user: str = Depends(get_current_user),
    ):
        """Desbloquear una IP"""
        try:
            await manager.ip_blocker.unblock_ip(ip)
            return JSONResponse(content={"message": f"IP {ip} desbloqueada correctamente", "ip": ip})
        except Exception as e:
            logger.error(f"Error desbloqueando IP {ip}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get(f"{dashboard_path}/api/export")
    async def export_report(
        user: str = Depends(get_current_user),
        format: str = "csv",
    ):
        """Exportar reporte de ataques"""
        try:
            # Obtener todos los ataques
            attacks = await manager.db.get_all_attacks()
            
            if format == "csv":
                # Generar CSV
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Encabezados
                writer.writerow([
                    "ID", "Timestamp", "Endpoint", "Method", "IP", "Country",
                    "Threat Type", "Severity", "Blocked", "Details"
                ])
                
                # Datos
                for attack in attacks:
                    writer.writerow([
                        attack.get("id"),
                        attack.get("timestamp"),
                        attack.get("endpoint"),
                        attack.get("method"),
                        attack.get("ip"),
                        attack.get("country"),
                        attack.get("threat_type"),
                        attack.get("severity"),
                        "Sí" if attack.get("blocked") else "No",
                        str(attack.get("details", {})),
                    ])
                
                # Devolver CSV
                csv_content = output.getvalue()
                output.close()
                
                return Response(
                    content=csv_content,
                    media_type="text/csv",
                    headers={
                        "Content-Disposition": f"attachment; filename=reporte_ataques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    }
                )
            
            elif format == "json":
                # Devolver JSON
                return JSONResponse(
                    content={"attacks": attacks, "total": len(attacks)},
                    headers={
                        "Content-Disposition": f"attachment; filename=reporte_ataques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    }
                )
            
            else:
                raise HTTPException(status_code=400, detail="Formato no soportado. Use 'csv' o 'json'")
        
        except Exception as e:
            logger.error(f"Error exportando reporte: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get(f"{dashboard_path}/api/trends")
    async def get_trends(
        user: str = Depends(get_current_user),
        hours: int = 24,
    ):
        """Obtener tendencias temporales de ataques"""
        try:
            trends = await manager.db.get_attack_trends(hours=hours)
            return JSONResponse(content={"trends": trends, "hours": hours})
        except Exception as e:
            logger.error(f"Error obteniendo tendencias: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    logger.info(f"Rutas del dashboard configuradas en {dashboard_path}")

