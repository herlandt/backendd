from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .serializers import DeviceTokenSerializer
from .models import DeviceToken
from .services import send_push

class RegistrarDeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ser = DeviceTokenSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response({"id": obj.id, "detail": "token registrado"}, status=status.HTTP_201_CREATED)

class EnviarNotificacionDemoView(APIView):
    """
    Admin-only. Envía una notificación de prueba:
      POST { "title": "Hola", "body": "Mensaje", "user_id": <opcional>, "data": {...} }
    """
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        title = request.data.get("title") or "Demo"
        body = request.data.get("body") or "Mensaje de prueba"
        data = request.data.get("data") or {}
        user_id = request.data.get("user_id")

        qs = DeviceToken.objects.filter(active=True)
        if user_id:
            qs = qs.filter(user_id=user_id)

        tokens = list(qs.values_list("token", flat=True))
        if not tokens:
            return Response({"sent": 0, "detail": "no hay tokens"}, status=status.HTTP_200_OK)

        res = send_push(tokens, title, body, data)
        return Response(res, status=status.HTTP_200_OK)

# notificaciones/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Dispositivo
from .serializers import DispositivoSerializer

class RegistrarDispositivoView(generics.CreateAPIView):
    """
    Endpoint para que la app móvil registre el token de un dispositivo
    y lo asocie con el usuario autenticado.
    """
    queryset = Dispositivo.objects.all()
    serializer_class = DispositivoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Asocia el dispositivo con el usuario que hace la petición
        token = serializer.validated_data.get('token_dispositivo')
        # Usamos get_or_create para no tener tokens duplicados
        Dispositivo.objects.get_or_create(token_dispositivo=token, defaults={'usuario': self.request.user})

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"detail": "Dispositivo registrado correctamente."}, status=status.HTTP_201_CREATED)