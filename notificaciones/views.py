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
