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

# En usuarios/serializers.py

# ... (otras importaciones)

class ResidenteWriteSerializer(serializers.Serializer):
    # --- MODIFICACIÓN 1: Añadir usuario_id y hacer los otros campos opcionales ---
    usuario_id = serializers.IntegerField(required=False)
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    propiedad_id = serializers.IntegerField() # Este sigue siendo requerido
    rol = serializers.ChoiceField(choices=Residente.ROL_CHOICES) # Y este también

    def validate(self, data):
        """
        Valida que se proporcione 'usuario_id' o 'username' y 'email', pero no ambos.
        """
        if 'usuario_id' in data and ('username' in data or 'email' in data):
            raise serializers.ValidationError("Proporciona 'usuario_id' o los datos del nuevo usuario ('username'/'email'), pero no ambos.")
        if 'usuario_id' not in data and ('username' not in data or 'email' not in data):
            raise serializers.ValidationError("Debes proporcionar un 'usuario_id' existente o 'username' y 'email' para un nuevo usuario.")
        return data

    def validate_username(self, value):
        # Esta validación solo se aplica si no estamos actualizando
        if not self.instance and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este nombre.")
        return value

    def create(self, validated_data):
        """
        --- MODIFICACIÓN 2: Lógica para manejar usuario existente o crear uno nuevo ---
        """
        user = None
        # CASO 1: Se proporciona el ID de un usuario existente
        if 'usuario_id' in validated_data:
            try:
                user = User.objects.get(pk=validated_data['usuario_id'])
            except User.DoesNotExist:
                raise serializers.ValidationError({"usuario_id": "No se encontró un usuario con este ID."})
        
        # CASO 2: Se crea un usuario nuevo
        else:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data.get('password') or User.objects.make_random_password()
            )

        # Finalmente, crea el perfil de Residente y lo asocia
        residente = Residente.objects.create(
            usuario=user,
            propiedad_id=validated_data['propiedad_id'],
            rol=validated_data['rol']
        )
        return residente

    def update(self, instance, validated_data):
        # Esta función de actualizar la dejamos como estaba
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
        # Esta función también la dejamos como estaba
        representation = {
            'id': instance.id,
            'rol': instance.rol,
            'usuario': {
                'id': instance.usuario.id,
                'username': instance.usuario.username,
                'email': instance.usuario.email
            }
        }
        if instance.propiedad:
             representation['propiedad'] = {
                'id': instance.propiedad.id,
                'numero_casa': instance.propiedad.numero_casa
            }
        else:
            representation['propiedad'] = None
            
        return representation
# Serializador necesario para otras vistas que puedas tener
class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
