from rest_framework import viewsets, generics, permissions
from django.contrib.auth.models import User
from .models import Residente
from .serializers import ResidenteSerializer, RegistroSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ResidenteViewSet(viewsets.ModelViewSet):
    queryset = Residente.objects.all()
    serializer_class = ResidenteSerializer

class RegistroView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistroSerializer
    permission_classes = [permissions.IsAdminUser]

class RegistrarDispositivoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        token = request.data.get('fcm_token')
        if not token:
            return Response({'error': 'FCM Token no fue proporcionado.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            residente = Residente.objects.get(usuario=request.user)
            residente.fcm_token = token
            residente.save()
            return Response({'status': 'Token registrado con éxito.'}, status=status.HTTP_200_OK)
        except Residente.DoesNotExist:
            return Response({'error': 'Este usuario no es un residente.'}, status=status.HTTP_404_NOT_FOUND)