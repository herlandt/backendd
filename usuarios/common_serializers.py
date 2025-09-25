# usuarios/common_serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers

# Este serializador es usado por otras apps, por eso vive en un fichero común.
class UserReadSerializer(serializers.ModelSerializer):
    """Muestra la información del usuario de forma segura y legible."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']