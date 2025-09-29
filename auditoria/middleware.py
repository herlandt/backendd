# en auditoria/middleware.py

class IPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Intenta obtener la IP desde la cabecera X-Forwarded-For (para proxies)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            # Si no, usa la IP de la conexión directa
            ip = request.META.get('REMOTE_ADDR')

        # Adjuntamos la IP al objeto request para usarla en cualquier vista
        request.ip_address = ip

        response = self.get_response(request)
        return response