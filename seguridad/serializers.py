from rest_framework import serializers
from .models import Visitante, Visita, Vehiculo

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['id', 'propiedad', 'placa', 'marca', 'modelo']

class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitante
        fields = ['id', 'nombre_completo', 'documento_identidad']

class VisitaSerializer(serializers.ModelSerializer):
    # Usamos el serializador del visitante para anidar la información
    visitante = VisitanteSerializer() 
    
    # Hacemos que la propiedad sea de solo lectura para mostrarla, pero no para crearla desde aquí
    propiedad = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Visita
        fields = [
            'id', 
            'propiedad', 
            'visitante', 
            'fecha_ingreso_programado', 
            'fecha_salida_programada',
            'ingreso_real',
            'salida_real'
        ]
        # Hacemos algunos campos de solo lectura, ya que se gestionan en el backend
        read_only_fields = ['ingreso_real', 'salida_real']

    def create(self, validated_data):
        # Extraemos los datos del visitante del JSON recibido
        visitante_data = validated_data.pop('visitante')
        
        # Buscamos si el visitante ya existe por su documento, si no, lo creamos.
        # Esto evita tener visitantes duplicados.
        visitante, created = Visitante.objects.get_or_create(
            documento_identidad=visitante_data['documento_identidad'],
            defaults={'nombre_completo': visitante_data['nombre_completo']}
        )
        
        # Creamos la visita asociándola con el visitante encontrado o recién creado
        visita = Visita.objects.create(visitante=visitante, **validated_data)
        return visita