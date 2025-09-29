from rest_framework import serializers
from condominio.models import Propiedad
from .models import PersonalMantenimiento, SolicitudMantenimiento


class PersonalMantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalMantenimiento
        fields = ["id", "nombre", "telefono", "especialidad", "activo"]


class SolicitudMantenimientoSerializer(serializers.ModelSerializer):
    # Lecturas “bonitas”
    solicitado_por = serializers.ReadOnlyField(source="solicitado_por.username")
    propiedad_numero = serializers.ReadOnlyField(source="propiedad.numero_casa")
    asignado_a_nombre = serializers.ReadOnlyField(source="asignado_a.nombre")

    # Escritura por ids
    propiedad_id = serializers.PrimaryKeyRelatedField(
        queryset=Propiedad.objects.all(), source="propiedad", write_only=True, required=True
    )
    asignado_a_id = serializers.PrimaryKeyRelatedField(
        queryset=PersonalMantenimiento.objects.filter(activo=True),
        source="asignado_a",
        allow_null=True,
        required=False,
        write_only=True,
    )

    # ⚠️ Habilitamos escritura de estado
    estado = serializers.ChoiceField(
        choices=SolicitudMantenimiento.ESTADOS, required=False
    )

    class Meta:
        model = SolicitudMantenimiento
        fields = [
            "id",
            "solicitado_por",
            "propiedad_numero",
            "titulo",
            "descripcion",
            "estado",
            "asignado_a_nombre",
            "fecha_creacion",
            "fecha_actualizacion",
            # ids de escritura
            "propiedad_id",
            "asignado_a_id",
        ]
        read_only_fields = ["fecha_creacion", "fecha_actualizacion", "solicitado_por"]

    def create(self, validated_data):
       
        return SolicitudMantenimiento.objects.create(**validated_data)
