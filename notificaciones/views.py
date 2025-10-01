from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .serializers import DeviceTokenSerializer, DispositivoSerializer, EnviarNotificacionRequestSerializer, NotificacionResponseSerializer
from .models import DeviceToken, Dispositivo
from .services import send_push

class RegistrarDeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceTokenSerializer  # Para documentación

    def post(self, request):
        ser = DeviceTokenSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(DeviceTokenSerializer(obj).data, status=status.HTTP_201_CREATED)

class EnviarNotificacionDemoView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = NotificacionResponseSerializer  # Para documentación

    def post(self, request):
        title = request.data.get("title") or "Demo"
        body  = request.data.get("body")  or "Mensaje de prueba"
        data  = request.data.get("data")  or {}
        user_id = request.data.get("user_id")

        qs = DeviceToken.objects.filter(active=True)
        if user_id:
            qs = qs.filter(user_id=user_id)

        tokens = list(qs.values_list("token", flat=True))
        if not tokens:
            return Response({"sent": 0, "note": "no hay tokens"}, status=200)

        res = send_push(tokens, title, body, data)
        return Response(res, status=200)


# Registrar dispositivo “físico” de la app (si lo quieres usar)
from rest_framework import generics, permissions

class RegistrarDispositivoView(generics.CreateAPIView):
    queryset = Dispositivo.objects.all()
    serializer_class = DispositivoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        token = serializer.validated_data["token_dispositivo"]
        Dispositivo.objects.get_or_create(
            token_dispositivo=token,
            defaults={"usuario": self.request.user, "activo": True},
        )
