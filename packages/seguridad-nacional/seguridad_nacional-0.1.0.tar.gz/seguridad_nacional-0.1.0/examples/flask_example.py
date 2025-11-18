"""
Ejemplo de uso de Seguridad Nacional con Flask
"""

from flask import Flask, jsonify, request
import seguridad_nacional as sn

# Crear aplicación Flask
app = Flask(__name__)

# Monitorear la aplicación automáticamente
# Esto agrega el middleware y todas las rutas del dashboard
try:
    sn.monitor(app, config_path="config.hackathon.yaml")
except:
    # Si no existe, usar configuración por defecto
    sn.monitor(app)

# Endpoints de ejemplo
@app.route("/")
def root():
    """Endpoint raíz"""
    return jsonify({"message": "Bienvenido a la API protegida"})


@app.route("/api/users", methods=["GET"])
def get_users():
    """Obtener usuarios"""
    return jsonify({
        "users": [
            {"id": 1, "name": "Juan"},
            {"id": 2, "name": "María"},
        ]
    })


@app.route("/api/users", methods=["POST"])
def create_user():
    """Crear usuario"""
    user = request.get_json()
    return jsonify({"message": "Usuario creado", "user": user})


@app.route("/api/data", methods=["GET"])
def get_data():
    """Obtener datos"""
    return jsonify({"data": "Información confidencial"})


# Ejecutar con: flask run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

