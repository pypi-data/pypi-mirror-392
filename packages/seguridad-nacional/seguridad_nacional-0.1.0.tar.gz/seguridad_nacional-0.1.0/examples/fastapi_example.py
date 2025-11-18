"""
Ejemplo de uso de Seguridad Nacional con FastAPI
"""

from fastapi import FastAPI
import seguridad_nacional as sn

# Crear aplicación FastAPI
app = FastAPI(title="API Protegida con Seguridad Nacional")

# Monitorear la aplicación automáticamente
# Esto agrega el middleware y todas las rutas del dashboard
# Para hackathon: usar análisis síncrono (bloquea inmediatamente)
# Si el archivo config.hackathon.yaml no existe, usa configuración por defecto
try:
    sn.monitor(app, config_path="config.hackathon.yaml")
except:
    # Si no existe, usar configuración por defecto
    sn.monitor(app)

# Endpoints de ejemplo
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Bienvenido a la API protegida"}


@app.get("/api/users")
async def get_users():
    """Obtener usuarios"""
    return {
        "users": [
            {"id": 1, "name": "Juan"},
            {"id": 2, "name": "María"},
        ]
    }


@app.post("/api/users")
async def create_user(user: dict):
    """Crear usuario"""
    return {"message": "Usuario creado", "user": user}


@app.get("/api/data")
async def get_data():
    """Obtener datos"""
    return {"data": "Información confidencial"}


# Ejecutar con: uvicorn examples.fastapi_example:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

