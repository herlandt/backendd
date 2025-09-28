from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Residente
from condominio.serializers import PropiedadSerializer
from .common_serializers import UserReadSerializer
# --- SERIALIZADORES PARA LEER DATOS (GET) ---

class ResidenteReadSerializer(serializers.ModelSerializer):
    usuario = UserReadSerializer(read_only=True)
    propiedad = PropiedadSerializer(read_only=True)
    
    class Meta:
        model = Residente
        fields = ['id', 'usuario', 'propiedad', 'rol']

class ResidenteReadSerializer(serializers.ModelSerializer):
    usuario = UserReadSerializer(read_only=True)
    propiedad = PropiedadSerializer(read_only=True)
    
    class Meta:
        model = Residente
        fields = ['id', 'usuario', 'propiedad', 'rol']


# --- SERIALIZADOR PARA ESCRIBIR DATOS (POST / PUT) ---

class ResidenteWriteSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    propiedad_id = serializers.IntegerField()
    rol = serializers.ChoiceField(choices=Residente.ROL_CHOICES)

    def validate_username(self, value):
        if self.instance:
            if User.objects.filter(username=value).exclude(pk=self.instance.usuario.pk).exists():
                raise serializers.ValidationError("Este nombre de usuario ya está en uso por otro residente.")
        elif User.objects.filter(username=value).exists():
             raise serializers.ValidationError("Este nombre de usuario ya existe.")
        return value

    def create(self, validated_data):
        """
        Lógica para CREAR un nuevo Residente y su Usuario.
        --- ¡CORRECCIÓN AQUÍ! ---
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data.get('password')
        )
        residente = Residente.objects.create(
            usuario=user,
            propiedad_id=validated_data['propiedad_id'],
            rol=validated_data['rol']
        )
        return residente

    def update(self, instance, validated_data):
        """Lógica para ACTUALIZAR un Residente y su Usuario."""
        user = instance.usuario
        user.username = validated_data.get('username', user.username)
        user.email = validated_data.get('email', user.email)
        
        password = validated_data.get('password')
        if password:
            user.set_password(password)
        user.save()

        instance.propiedad_id = validated_data.get('propiedad_id', instance.propiedad_id)
        instance.rol = validated_data.get('rol', instance.rol)
        instance.save()

        return instance

    def to_representation(self, instance):
        """Define cómo se debe mostrar el objeto después de crearlo o actualizarlo."""
        return {
            'id': instance.id,
            'rol': instance.rol,
            'usuario': {
                'id': instance.usuario.id,
                'username': instance.usuario.username,
                'email': instance.usuario.email
            },
            'propiedad': {
                'id': instance.propiedad.id,
                'numero_casa': instance.propiedad.numero_casa
            }
        }

# Serializador necesario para otras vistas que puedas tener
class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
