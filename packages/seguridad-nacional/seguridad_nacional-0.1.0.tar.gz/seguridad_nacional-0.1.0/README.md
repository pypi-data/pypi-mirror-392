# 🔒 Seguridad Nacional - Librería de Seguridad

> **Protección automatizada de endpoints para aplicaciones Python**

Una librería Python diseñada para proteger aplicaciones web salvadoreñas contra ciberataques masivos. Con más de **600,000 ciberataques registrados en El Salvador durante 2024**, esta herramienta proporciona monitoreo continuo, detección de vulnerabilidades y bloqueo automático de amenazas.

## 🎯 Problema que Resuelve

El Salvador enfrenta:
- **600,000+ ciberataques en 2024** (Constella Intelligence, Mayo 2024)
- **Solo ~300 profesionales certificados** en ciberseguridad
- **Brechas masivas de datos** (5M ciudadanos, PGR, Movistar)
- **Incapacidad de defender** infraestructura crítica y datos personales

## ✨ Características

### 🔍 Monitoreo Continuo
- Monitoreo automático de todos los endpoints
- Análisis en tiempo real de requests y parámetros
- Detección de patrones sospechosos e inusuales

### 🛡️ Protección contra Ataques Comunes
- **SQL Injection**: Detección y bloqueo automático
- **XSS (Cross-Site Scripting)**: Validación y sanitización
- **Ataques por IP**: Identificación de comportamientos anómalos
- **Robo de datos**: Detección de intentos de extracción masiva

### 🚫 Bloqueo Automático
- Bloqueo automático de IPs maliciosas
- Corte de conexiones sospechosas
- Reglas configurables de seguridad por severidad

### 📊 Dashboard de Visualización
- Mapa mundial de ataques (heatmap por IP/país)
- Endpoints más vulnerables
- Tipos de vulnerabilidades más frecuentes
- Estadísticas en tiempo real
- Historial de ataques con filtros

## 🚀 Instalación

```bash
pip install seguridad-nacional
```

## 💻 Uso Básico

### FastAPI

```python
from fastapi import FastAPI
import seguridad_nacional as sn

app = FastAPI()

# Proteger la aplicación (automático)
sn.monitor(app)

@app.get("/api/users")
async def get_users():
    return {"users": []}
```

### Flask

```python
from flask import Flask
import seguridad_nacional as sn

app = Flask(__name__)

# Proteger la aplicación (automático)
sn.monitor(app)

@app.route("/api/users")
def get_users():
    return {"users": []}
```

### Django

En `settings.py`:

```python
MIDDLEWARE = [
    # ... otros middlewares ...
    'seguridad_nacional.middleware.django_middleware.DjangoSecurityMiddleware',
]
```

O usar la función `monitor()`:

```python
# En tu archivo de configuración
import seguridad_nacional as sn
sn.monitor(framework='django')
```

### Decorador Manual

También puedes usar decoradores manuales (FastAPI/Flask):

```python
@sn.protect
@app.post("/api/data")
async def receive_data(data: dict):
    return {"status": "ok"}
```

### Configuración

Crea un archivo `.env`:

```env
SEGURIDAD_NACIONAL_ENABLED=true
SEGURIDAD_NACIONAL_DB_PATH=./seguridad.db
SEGURIDAD_NACIONAL_DASHBOARD_USER=admin
SEGURIDAD_NACIONAL_DASHBOARD_PASSWORD=admin123
SEGURIDAD_NACIONAL_BLOCK_THRESHOLD=25
```

O crea un archivo `config.yaml`:

```yaml
seguridad:
  enabled: true
  db_path: ./seguridad.db
  block_threshold: 25
  dashboard:
    user: admin
    password: admin123
  whitelist:
    ips: []
    patterns: []
```

## 📋 Requisitos

- Python 3.8+
- **Soporta múltiples frameworks:**
  - ✅ FastAPI (completamente implementado)
  - ✅ Flask (completamente implementado)
  - ✅ Django (completamente implementado)

## 🏗️ Arquitectura

```
seguridad_nacional/
├── core/           # Núcleo de la librería
├── detectors/      # Detectores de vulnerabilidades
├── middleware/     # Middlewares para frameworks
├── dashboard/      # API y frontend del dashboard
├── storage/        # Persistencia (SQLite)
├── utils/          # Utilidades (geolocalización, etc.)
└── config/         # Configuración
```

## 📈 Roadmap

- [x] Detección básica de SQL Injection
- [x] Detección de XSS
- [x] Bloqueo automático de IPs
- [x] Dashboard completo
- [ ] Integración con normativas salvadoreñas
- [ ] Machine Learning para detección avanzada

## 📄 Licencia

MIT License

## 🤝 Contribuciones

Este proyecto es parte de un hackathon de Seguridad Nacional Inteligente auspiciado por Key Institute (El Salvador).

## 📞 Contacto

Para reportar vulnerabilidades o sugerencias, por favor abra un issue.

---

**Desarrollado para fortalecer la ciberseguridad en El Salvador 🇸🇻**

