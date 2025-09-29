"""
Django settings for config project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / Debug (ojo en producción) ---
SECRET_KEY = 'django-insecure-_add0b!8@6c@+*uvhp!mf@=#09m=mzsauiv_c$&35pfs$!t0(!'
DEBUG = True
ALLOWED_HOSTS = ['10.0.2.2', 'localhost', '127.0.0.1', '192.168.0.18']

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
    "notificaciones",
]
FCM_SERVER_KEY = 'xhdePFTJ5JCcWRkbXXaGoEq_6XUOTlFBWa7GomXTt_0'
NOTIF_FAKE_SEND = True
# config/settings.py

# ... (toda tu configuración existente) ...

# ========= CLAVE DE API PARA LA CÁMARA DE IA =========
CAMARA_API_KEY = "MI_CLAVE_SUPER_SECRETA_12345"
# --- Middleware (corsheaders antes de CommonMiddleware) ---
MIDDLEWARE = [
    
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

# --- Base de datos ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'condominio_db',
        'USER': 'postgres',
        'PASSWORD': '12345678',
        'HOST': 'localhost',
        'PORT': '5432',
    }
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
    "http://localhost:3000",
]
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
    # 'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SECURITY': [{'TokenAuth': []}],
}

AWS_REKOGNITION_COLLECTION_ID = "condominio_residentes"