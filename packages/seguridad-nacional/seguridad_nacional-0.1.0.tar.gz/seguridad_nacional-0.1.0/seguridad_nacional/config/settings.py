"""Configuración de la librería"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuración de Seguridad Nacional"""
    
    # General
    enabled: bool = Field(default=True, description="Habilitar/deshabilitar la librería")
    debug: bool = Field(default=False, description="Modo debug")
    
    # Database
    db_path: str = Field(default="./seguridad.db", description="Ruta de la base de datos SQLite")
    
    # Blocking
    block_threshold: int = Field(default=25, description="Número de intentos antes de bloquear")
    block_duration_30min: bool = Field(default=True, description="Bloqueo de 30 minutos para severidad baja")
    block_duration_1h: bool = Field(default=True, description="Bloqueo de 1 hora para severidad media")
    block_duration_indefinite: bool = Field(default=True, description="Bloqueo indefinido para severidad alta")
    
    # Analysis
    analysis_timeout: int = Field(default=100, description="Timeout de análisis en milisegundos")
    async_analysis: bool = Field(default=True, description="Análisis asíncrono")
    
    # Dashboard
    dashboard_enabled: bool = Field(default=True, description="Habilitar dashboard")
    dashboard_path: str = Field(default="/seguridad", description="Ruta base del dashboard")
    dashboard_user: str = Field(default="admin", description="Usuario del dashboard")
    dashboard_password: str = Field(default="admin123", description="Contraseña del dashboard")
    dashboard_port: Optional[int] = Field(default=None, description="Puerto del dashboard (None = mismo que app)")
    
    # Geolocation
    geolocation_enabled: bool = Field(default=True, description="Habilitar geolocalización")
    geolocation_api: str = Field(default="ip-api", description="API de geolocalización (ip-api, ipapi)")
    geolocation_cache_enabled: bool = Field(default=True, description="Habilitar caché de geolocalización")
    geolocation_cache_ttl: int = Field(default=86400, description="TTL del caché en segundos (24h)")
    
    # Whitelist
    whitelist_ips: List[str] = Field(default_factory=list, description="Lista de IPs en whitelist")
    whitelist_patterns: List[str] = Field(default_factory=list, description="Lista de patrones en whitelist")
    
    # Detection
    sql_injection_enabled: bool = Field(default=True, description="Habilitar detección de SQL Injection")
    xss_enabled: bool = Field(default=True, description="Habilitar detección de XSS")
    suspicious_behavior_enabled: bool = Field(default=True, description="Habilitar detección de comportamientos sospechosos")
    
    # Logging
    log_level: str = Field(default="INFO", description="Nivel de logging")
    log_file: Optional[str] = Field(default=None, description="Archivo de log (None = solo consola)")
    
    class Config:
        env_prefix = "SEGURIDAD_NACIONAL_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia global de configuración
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Obtener la configuración global"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def load_settings_from_file(config_path: Optional[str] = None) -> Settings:
    """Cargar configuración desde archivo YAML"""
    try:
        import yaml
    except ImportError:
        # Si YAML no está instalado, retornar configuración por defecto
        logger.warning("PyYAML no está instalado. Usando configuración por defecto.")
        return get_settings()
    
    if config_path is None:
        config_path = "config.yaml"
    
    config_file = Path(config_path)
    if not config_file.exists():
        return get_settings()
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        
        # Cargar configuración desde YAML
        if "seguridad" in config_data:
            seguridad_config = config_data["seguridad"]
            
            # Actualizar configuración
            settings = get_settings()
            for key, value in seguridad_config.items():
                if hasattr(settings, key) and key != "whitelist":
                    setattr(settings, key, value)
            
            # Whitelist
            if "whitelist" in seguridad_config:
                whitelist = seguridad_config["whitelist"]
                if "ips" in whitelist:
                    settings.whitelist_ips = whitelist["ips"]
                if "patterns" in whitelist:
                    settings.whitelist_patterns = whitelist["patterns"]
            
            return settings
    except Exception as e:
        logger.error(f"Error cargando configuración desde {config_path}: {e}")
    
    return get_settings()

