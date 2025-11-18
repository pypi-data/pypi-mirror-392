"""
Script para probar ataques y verificar que la librería los detecta
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def check_server():
    """Verificar que el servidor está corriendo"""
    try:
        requests.get(BASE_URL, timeout=2)
        return True
    except:
        print("❌ Error: El servidor no está corriendo")
        print("   Ejecuta: uvicorn examples.fastapi_example:app --reload")
        return False

def test_sql_injection():
    """Probar inyección SQL"""
    print("Testing SQL Injection...")
    
    # Ataque SQL Injection en parámetros
    response = requests.get(f"{BASE_URL}/api/users", params={
        "id": "1' OR '1'='1"
    })
    print(f"SQL Injection en params: {response.status_code}")
    
    # Ataque SQL Injection en body
    response = requests.post(f"{BASE_URL}/api/users", json={
        "name": "'; DROP TABLE users; --"
    })
    print(f"SQL Injection en body: {response.status_code}")
    
    time.sleep(1)


def test_xss():
    """Probar XSS"""
    print("Testing XSS...")
    
    # Ataque XSS en parámetros
    response = requests.get(f"{BASE_URL}/api/users", params={
        "search": "<script>alert('XSS')</script>"
    })
    print(f"XSS en params: {response.status_code}")
    
    # Ataque XSS en body
    response = requests.post(f"{BASE_URL}/api/users", json={
        "name": "<img src=x onerror=alert('XSS')>"
    })
    print(f"XSS en body: {response.status_code}")
    
    time.sleep(1)


def test_suspicious_behavior():
    """Probar comportamiento sospechoso"""
    print("Testing Suspicious Behavior...")
    
    # Múltiples requests rápidos
    for i in range(30):
        response = requests.get(f"{BASE_URL}/api/users")
        print(f"Request {i+1}: {response.status_code}")
        time.sleep(0.1)
    
    time.sleep(1)


def test_normal_request():
    """Probar request normal"""
    print("Testing Normal Request...")
    
    response = requests.get(f"{BASE_URL}/api/users")
    print(f"Normal request: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Seguridad Nacional")
    print("=" * 50)
    
    # Verificar que el servidor está corriendo
    if not check_server():
        sys.exit(1)
    
    # Probar request normal primero
    test_normal_request()
    time.sleep(2)
    
    # Probar ataques
    test_sql_injection()
    time.sleep(1)
    test_xss()
    time.sleep(1)
    test_suspicious_behavior()
    
    print("=" * 50)
    print("Tests completados")
    print("=" * 50)
    print("\n📊 Ve al dashboard en: http://localhost:8000/seguridad/dashboard")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\n💡 Tip: El dashboard se actualiza automáticamente cada 10 segundos")

