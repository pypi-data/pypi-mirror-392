"""Servicio de geolocalización de IPs"""

import httpx
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

from seguridad_nacional.config.settings import Settings

logger = logging.getLogger(__name__)


class GeolocationService:
    """Servicio de geolocalización usando IP-API"""
    
    def __init__(self, settings: Settings):
        """Inicializar el servicio de geolocalización"""
        self.settings = settings
        self.api = settings.geolocation_api
        self.cache: Dict[str, Dict] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.cache_ttl = settings.geolocation_cache_ttl
        
        # URL base según la API
        if self.api == "ip-api":
            self.base_url = "http://ip-api.com/json"
        elif self.api == "ipapi":
            self.base_url = "https://ipapi.co"
        else:
            self.base_url = "http://ip-api.com/json"  # Por defecto
    
    async def get_location(self, ip: str) -> Dict[str, Optional[str]]:
        """Obtener ubicación de una IP"""
        # Verificar caché
        if self.settings.geolocation_cache_enabled:
            if ip in self.cache:
                timestamp = self.cache_timestamps.get(ip)
                if timestamp and datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                    return self.cache[ip]
        
        try:
            if self.api == "ip-api":
                location = await self._get_location_ipapi(ip)
            elif self.api == "ipapi":
                location = await self._get_location_ipapi_co(ip)
            else:
                location = await self._get_location_ipapi(ip)
            
            # Guardar en caché
            if self.settings.geolocation_cache_enabled:
                self.cache[ip] = location
                self.cache_timestamps[ip] = datetime.now()
            
            return location
        except Exception as e:
            logger.error(f"Error obteniendo geolocalización para IP {ip}: {e}")
            return {
                "country": None,
                "country_code": None,
                "region": None,
                "city": None,
                "lat": None,
                "lon": None,
            }
    
    async def _get_location_ipapi(self, ip: str) -> Dict[str, Optional[str]]:
        """Obtener ubicación usando IP-API (gratis, sin registro)"""
        # Manejar localhost/127.0.0.1 de manera especial
        # Para el hackathon, usar "El Salvador" para localhost
        if ip in ["127.0.0.1", "localhost", "::1", "0.0.0.0"]:
            return {
                "country": "El Salvador",  # Usar El Salvador para localhost en el hackathon
                "country_code": "SV",
                "region": "San Salvador",
                "city": "San Salvador",
                "lat": "13.7942",
                "lon": "-88.8965",
            }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/{ip}")
                if response.status_code == 200:
                    data = response.json()
                    # Verificar si la respuesta fue exitosa
                    if data.get("status") == "fail":
                        # IP reservada o privada, tratar como local
                        if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172.16."):
                            return {
                                "country": "Local",
                                "country_code": "LOC",
                                "region": "Private Network",
                                "city": "Local",
                                "lat": "13.7942",  # El Salvador
                                "lon": "-88.8965",
                            }
                        # Para localhost, usar El Salvador
                        return {
                            "country": "El Salvador",
                            "country_code": "SV",
                            "region": "San Salvador",
                            "city": "San Salvador",
                            "lat": "13.7942",
                            "lon": "-88.8965",
                        }
                    return {
                        "country": data.get("country"),
                        "country_code": data.get("countryCode"),
                        "region": data.get("regionName"),
                        "city": data.get("city"),
                        "lat": str(data.get("lat")) if data.get("lat") else None,
                        "lon": str(data.get("lon")) if data.get("lon") else None,
                    }
                else:
                    raise Exception(f"Error en IP-API: {response.status_code}")
            except Exception as e:
                logger.warning(f"Error obteniendo geolocalización para {ip}: {e}")
                # Si falla, usar El Salvador por defecto para localhost
                if ip in ["127.0.0.1", "localhost", "::1"]:
                    return {
                        "country": "El Salvador",
                        "country_code": "SV",
                        "region": "San Salvador",
                        "city": "San Salvador",
                        "lat": "13.7942",
                        "lon": "-88.8965",
                    }
                raise
    
    async def _get_location_ipapi_co(self, ip: str) -> Dict[str, Optional[str]]:
        """Obtener ubicación usando ipapi.co (requiere registro)"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{self.base_url}/{ip}/json/")
            if response.status_code == 200:
                data = response.json()
                return {
                    "country": data.get("country_name"),
                    "country_code": data.get("country_code"),
                    "region": data.get("region"),
                    "city": data.get("city"),
                    "lat": str(data.get("latitude")) if data.get("latitude") else None,
                    "lon": str(data.get("longitude")) if data.get("longitude") else None,
                }
            else:
                raise Exception(f"Error en ipapi.co: {response.status_code}")
    
    def clear_cache(self):
        """Limpiar caché"""
        self.cache.clear()
        self.cache_timestamps.clear()

