"""
Django settings for config project.fig
"""

from pathlib import Path
import dj_database_url
import os
from decouple import config
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / Debug (ojo en producción) ---
SECRET_KEY = config('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = [
    '10.0.2.2',       # Android Emulator (AVD)
    '10.0.2.15',      # Android Emulator alternativo
    '10.0.2.16',      # Android Emulator host gateway
    'localhost', 
    '127.0.0.1', 
    '192.168.0.18',
    '192.168.0.5',    # Tu IP local detectada
    '172.18.128.1',   # Tu IP alternativa detectada
    '0.0.0.0',        # Permite todas las IPs (solo para desarrollo)
]
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
# --- Apps ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto
    'usuarios',
    'condominio',
    'finanzas',
    'seguridad',
    'mantenimiento',
    
    'auditoria.apps.AuditoriaConfig',  # Asegúrate de usar la configuración correcta
    # Terceros
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'django_filters',  # Añadido para filtros avanzados
    "notificaciones",
]
FCM_SERVER_KEY = 'xhdePFTJ5JCcWRkbXXaGoEq_6XUOTlFBWa7GomXTt_0'
NOTIF_FAKE_SEND = True

# Modelo de usuario personalizado
# AUTH_USER_MODEL = 'usuarios.User'  # Comentado por ahora para evitar problemas de migración
# --- Middleware (corsheaders antes de CommonMiddleware) ---
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'auditoria.middleware.IPMiddleware', 

    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # bien aquí
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
# Si usas ASGI (Daphne), mantén también config.asgi:application en tu comando.

import dj_database_url

# ...
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3', # <- Base de datos falsa si no hay DATABASE_URL
        conn_max_age=600
    )
}
# --- Validadores de password ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- CORS ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",    # Para desarrollo React/Next.js
    "http://localhost:5173",    # Para desarrollo con Vite/React
    "http://127.0.0.1:5173",    # Alternativa localhost
    "http://127.0.0.1:3000",    # Alternativa localhost
]

# --- CSRF ---
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]


# Añadir el host de Render a las listas de confianza si existe
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
if RENDER_EXTERNAL_URL:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME) # Este ya lo tenías
    CORS_ALLOWED_ORIGINS.append(RENDER_EXTERNAL_URL)
    CSRF_TRUSTED_ORIGINS.append(RENDER_EXTERNAL_URL)
# Si usas cookies de sesión desde el front:
# CORS_ALLOW_CREDENTIALS = True
# O para puertos dinámicos:
# CORS_ALLOWED_ORIGIN_REGEXES = [r"^http://localhost:\d+$"]

# --- Internacionalización ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
# ... (otras configuraciones)

# --- CONFIGURACIÓN DE PASARELA DE PAGOS ---
PAGOSNET_API_URL = 'https://servicios.pagosnet.com/api/v2/' # URL de prueba
PAGOSNET_EMAIL = 'tu_email_de_comercio@empresa.com'
PAGOSNET_PASSWORD = 'tu_password_de_comercio'
# --- Static ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # <--- AÑADE ESTA LÍNEA
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- DRF ---
# backend/config/settings.py
# backend/config/settings.py
REST_FRAMEWORK = {
    # Autenticación: usamos Token primero para que los tests con "HTTP_AUTHORIZATION: Token <key>" funcionen siempre
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],

    # Por defecto, todo requiere autenticación (los tests de permisos lo esperan)
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],

    # Filtros y backends por defecto
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],

    # Throttling de alcance (ScopedRateThrottle) para los endpoints de seguridad
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "control_acceso": "30/minute",
        "control_salida": "30/minute",
    },

    # Esquema OpenAPI (drf-spectacular)
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# --- drf-spectacular ---
SPECTACULAR_SETTINGS = {
    'TITLE': 'Condominio API',
    'DESCRIPTION': 'Endpoints para seguridad, finanzas, mantenimiento, usuarios.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # Para abrir docs sin auth (opcional):
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SECURITY': [{'TokenAuth': []}],
}

AWS_REKOGNITION_COLLECTION_ID = "condominio_residentes"

# --- CLAVE DE API PARA LA CÁMARA DE IA ---
SECURITY_API_KEY = "MI_CLAVE_SUPER_SECRETA_12345"

# --- CONFIGURACIÓN DE STRIPE ---
# Claves de Stripe (deben estar en variables de entorno por seguridad)
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET')

# La configuración de stripe.api_key se hace en las vistas para evitar errores de importación