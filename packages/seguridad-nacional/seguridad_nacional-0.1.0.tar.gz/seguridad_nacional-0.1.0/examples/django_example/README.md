# Ejemplo de Django con Seguridad Nacional

## Configuración

### 1. Instalar dependencias

```bash
pip install django seguridad-nacional
```

### 2. Configurar settings.py

Agrega el middleware a `MIDDLEWARE`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Agregar middleware de Seguridad Nacional
    'seguridad_nacional.middleware.django_middleware.DjangoSecurityMiddleware',
]
```

### 3. Configurar URLs (opcional, para dashboard)

En `urls.py` principal:

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    # Dashboard de seguridad (opcional)
    path('seguridad/', include('seguridad_nacional.dashboard.django_urls')),
]
```

### 4. Usar en tus vistas

```python
# views.py
from django.http import JsonResponse

def get_users(request):
    return JsonResponse({"users": []})

def create_user(request):
    # La protección es automática con el middleware
    return JsonResponse({"status": "created"})
```

## Ejecutar

```bash
python manage.py runserver
```

## Acceder al Dashboard

```
http://localhost:8000/seguridad/dashboard
Usuario: admin
Contraseña: admin123
```

