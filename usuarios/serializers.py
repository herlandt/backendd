# Fichero: usuarios/serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Residente
from condominio.serializers import PropiedadSerializer
from .common_serializers import UserSerializer

class ResidenteSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()
    propiedad = PropiedadSerializer(read_only=True)
    propiedad_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Residente
        fields = ['id', 'usuario', 'propiedad', 'rol', 'propiedad_id']
        read_only_fields = ['propiedad']

    def create(self, validated_data):
        user_data = validated_data.pop('usuario')
        password = user_data.pop('password', None)
        
        # Validar si el usuario o email ya existen antes de crear
        if User.objects.filter(username=user_data['username']).exists():
            raise serializers.ValidationError({'detail': 'Ya existe un usuario con este username.'})
        if User.objects.filter(email=user_data['email']).exists():
            raise serializers.ValidationError({'detail': 'Ya existe un usuario con este email.'})

        user = User.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()
            
        residente = Residente.objects.create(usuario=user, **validated_data)
        return residente

    def update(self, instance, validated_data):
        user_data = validated_data.get('usuario', {})
        user = instance.usuario

        # Validar username y email contra OTROS usuarios (excluyendo el actual)
        new_username = user_data.get('username')
        if new_username and new_username != user.username and User.objects.filter(username=new_username).exists():
            raise serializers.ValidationError({'detail': 'Ya existe otro usuario con este username.'})

        new_email = user_data.get('email')
        if new_email and new_email != user.email and User.objects.filter(email=new_email).exists():
            raise serializers.ValidationError({'detail': 'Ya existe otro usuario con este email.'})

        # Actualiza los campos del usuario
        user.username = new_username or user.username
        user.email = new_email or user.email
        
        password = user_data.get('password')
        if password:
            user.set_password(password)
        
        user.save()

        # Actualiza los campos del residente
        instance.propiedad_id = validated_data.get('propiedad_id', instance.propiedad_id)
        instance.rol = validated_data.get('rol', instance.rol)
        instance.save()

        return instance

class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user