from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import DeviceToken, Dispositivo
from .serializers import DeviceTokenSerializer, DispositivoSerializer
from .services import send_push  # asumiendo que ya lo tienes

class RegistrarDeviceTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = DeviceTokenSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj, created = DeviceToken.objects.update_or_create(
            token=ser.validated_data["token"],
            defaults={
                "user": request.user,
                "platform": ser.validated_data.get("platform", "web"),
                "active": True,
            },
        )
        return Response(DeviceTokenSerializer(obj).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class RegistrarDispositivoView(generics.CreateAPIView):
    queryset = Dispositivo.objects.all()
    serializer_class = DispositivoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        token = serializer.validated_data["token_dispositivo"]
        Dispositivo.objects.update_or_create(
            token_dispositivo=token,
            defaults={"usuario": self.request.user, "activo": True},
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"detail": "Dispositivo registrado correctamente."},
                        status=status.HTTP_201_CREATED)


class EnviarNotificacionDemoView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        title = request.data.get("title", "Demo")
        body = request.data.get("body", "Mensaje de prueba")
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
