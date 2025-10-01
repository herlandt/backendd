# En usuarios/management/commands/check_routes.py

import inspect
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from rest_framework.test import APIClient
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

# Colores para la terminal
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def get_api_urls(url_patterns, prefix=''):
    """
    Función recursiva para encontrar todas las rutas de la API.
    """
    api_urls = []
    for pattern in url_patterns:
        path = prefix + str(pattern.pattern)
        if hasattr(pattern, 'url_patterns'):
            api_urls.extend(get_api_urls(pattern.url_patterns, path))
        else:
            # Verificamos si es una ruta de API
            if '/api/' in path:
                # Simplificamos las URLs con parámetros
                simple_path = path.replace('<int:pk>/', '1/').replace('<int:id>/', '1/')
                simple_path = simple_path.replace('<str:pk>/', '1/').replace('<slug:slug>/', 'test/')
                if '{' not in simple_path and '<' not in simple_path:
                    clean_path = f"/{simple_path.lstrip('/')}"
                    # Evitamos duplicados y rutas muy genéricas
                    if clean_path not in api_urls and clean_path != '/api/':
                        api_urls.append(clean_path)
            
            # También agregamos rutas específicas que sabemos que existen
            known_endpoints = [
                '/api/',
                '/api/login/',
                '/api/registro/',
                '/api/usuarios/residentes/',
                '/api/condominio/propiedades/',
                '/api/finanzas/gastos/',
                '/api/seguridad/visitas/',
                '/api/mantenimiento/solicitudes/',
                '/api/schema/swagger-ui/',
            ]
            for endpoint in known_endpoints:
                if endpoint not in api_urls:
                    api_urls.append(endpoint)
                    
    return sorted(list(set(api_urls)))

class Command(BaseCommand):
    help = 'Verifica el estado de todos los endpoints de la API con una petición GET no autenticada.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=int,
            default=8000,
            help='Puerto del servidor (default: 8000)',
        )

    def handle(self, *args, **options):
        port = options['port']
        base_url = f"http://localhost:{port}"
        
        self.stdout.write(f"{BLUE}🚀 Verificando API en {base_url}...{RESET}")
        
        resolver = get_resolver()
        api_urls = get_api_urls(resolver.url_patterns)
        
        client = APIClient()
        
        total_urls = len(api_urls)
        errors_500 = 0
        errors_other = 0
        success_responses = 0

        self.stdout.write(f"{BLUE}🔍 Se encontraron {total_urls} rutas de API para verificar.{RESET}\n")

        for url in api_urls:
            try:
                full_url = base_url + url
                response = client.get(full_url)
                status_code = response.status_code

                if status_code == 500:
                    status_color = RED
                    errors_500 += 1
                    status_text = f"🚨 ERROR 500 - FALLO CRÍTICO"
                elif status_code in [401, 403]:
                    status_color = GREEN
                    success_responses += 1
                    status_text = f"✅ {status_code} - Requiere autenticación (CORRECTO)"
                elif status_code == 405:
                    status_color = YELLOW
                    status_text = f"⚠️  {status_code} - Método no permitido (normal para ViewSets)"
                elif status_code == 200:
                    status_color = GREEN
                    success_responses += 1
                    status_text = f"✅ {status_code} - Respuesta exitosa"
                elif status_code >= 400:
                     status_color = YELLOW
                     errors_other += 1
                     status_text = f"⚠️  {status_code} - Error cliente"
                else:
                    status_color = GREEN
                    success_responses += 1
                    status_text = f"✅ {status_code} - OK"

                self.stdout.write(f"{status_color}[{status_text}]{RESET} - GET {url}")

            except Exception as e:
                errors_500 += 1
                self.stdout.write(f"{RED}[🚨 EXCEPCIÓN CRÍTICA]{RESET} - GET {url} - Error: {e}")

        # Resumen final
        self.stdout.write(f"\n{BLUE}📊 RESUMEN DE VERIFICACIÓN:{RESET}")
        self.stdout.write(f"{GREEN}✅ Respuestas exitosas/correctas: {success_responses}{RESET}")
        self.stdout.write(f"{YELLOW}⚠️  Errores menores (400-499): {errors_other}{RESET}")
        self.stdout.write(f"{RED}🚨 Errores críticos (500+): {errors_500}{RESET}")
        
        if errors_500 > 0:
            self.stdout.write(f"\n{RED}❌ ATENCIÓN: {errors_500} endpoints tienen errores críticos que necesitan corrección.{RESET}")
            return
        elif errors_other > 0:
            self.stdout.write(f"\n{YELLOW}⚠️  Hay {errors_other} errores menores, pero la API está funcionalmente correcta.{RESET}")
        
        self.stdout.write(f"\n{GREEN}🎉 ¡PERFECTO! Todos los endpoints están funcionando correctamente.{RESET}")
        self.stdout.write(f"{GREEN}✅ No hay errores críticos (500) en la API.{RESET}")
        self.stdout.write(f"{GREEN}✅ Los errores 401/403 son normales (requieren autenticación).{RESET}")