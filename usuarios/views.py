# Fichero: usuarios/views.py

from rest_framework import viewsets, generics, permissions
from django.contrib.auth.models import User
from .models import Residente
# CORRECCIÓN: Importamos ambos serializadores que vamos a crear
from .serializers import ResidenteReadSerializer, ResidenteWriteSerializer, RegistroSerializer 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, permissions
from .models import Residente
from .serializers import ResidenteReadSerializer, ResidenteWriteSerializer, RegistroSerializer

class ResidenteViewSet(viewsets.ModelViewSet):
    queryset = Residente.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ResidenteWriteSerializer
        return ResidenteReadSerializer

    # --- ¡LA SOLUCIÓN ESTÁ AQUÍ! ---
    def perform_destroy(self, instance):
        # 'instance' es el objeto Residente que se va a eliminar.
        # Obtenemos el usuario asociado y lo eliminamos primero.
        user = instance.usuario
        # El objeto Residente se eliminará automáticamente en cascada
        # porque el 'on_delete' está en el modelo User.
        user.delete()
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