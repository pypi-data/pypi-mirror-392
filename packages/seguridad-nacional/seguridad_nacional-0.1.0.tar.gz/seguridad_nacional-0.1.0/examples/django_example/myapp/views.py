"""
Ejemplo de vistas Django con Seguridad Nacional
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def root(request):
    """Endpoint raíz"""
    return JsonResponse({"message": "Bienvenido a la API protegida"})


def get_users(request):
    """Obtener usuarios"""
    return JsonResponse({
        "users": [
            {"id": 1, "name": "Juan"},
            {"id": 2, "name": "María"},
        ]
    })


@csrf_exempt
def create_user(request):
    """Crear usuario"""
    if request.method == "POST":
        try:
            user = json.loads(request.body)
            return JsonResponse({"message": "Usuario creado", "user": user})
        except:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


def get_data(request):
    """Obtener datos"""
    return JsonResponse({"data": "Información confidencial"})

