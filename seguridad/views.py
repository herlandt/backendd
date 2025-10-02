# en seguridad/views.py

import csv
import boto3
from datetime import timedelta
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from rest_framework import status, viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

# Importaciones locales (de tu app)
from .models import Vehiculo, Visita, EventoSeguridad, Visitante, Deteccion
from .serializers import (
    ConsultaPlacaSerializer, 
    VisitaSerializer, 
    VehiculoSerializer, 
    VisitanteSerializer, 
    EventoSeguridadSerializer,
    DeteccionSerializer,
    ControlAccesoResponseSerializer,
    DashboardResumenResponseSerializer,
    DashboardSeriesResponseSerializer,
    TopVisitantesResponseSerializer,
    SimpleOperationResponseSerializer
)
from auditoria.eventos import notificar_visitante_registrado, notificar_acceso_vehicular
from .permissions import HasAPIKey
from usuarios.models import Residente
from usuarios.permissions import IsPropietario, IsPersonalSeguridad

# --- Vistas de Control de Acceso y Personalizadas ---

class ControlAccesoVehicularView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "control_acceso"
    serializer_class = ControlAccesoResponseSerializer  # Para documentación

    def _handle_ingreso(self, placa):
        ahora = timezone.now()
        try:
            vehiculo = Vehiculo.objects.get(placa__iexact=placa)
        except Vehiculo.DoesNotExist:
            return Response({"detail": f"Placa '{placa}' no encontrada."}, status=status.HTTP_403_FORBIDDEN)

        if vehiculo.propiedad:
            return Response({"detail": "Acceso permitido para residente.", "tipo": "residente"}, status=status.HTTP_200_OK)

        visita = Visita.objects.filter(
            visitante__vehiculos=vehiculo,
            ingreso_real__isnull=True,
            fecha_ingreso_programado__lte=ahora,
            fecha_salida_programada__gte=ahora
        ).first()

        if not visita:
            return Response({"detail": "Visitante sin visita programada vigente."}, status=status.HTTP_403_FORBIDDEN)
        
        visita.ingreso_real = ahora
        visita.save()
        return Response({"detail": "Acceso permitido para visitante.", "tipo": "visitante"}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ConsultaPlacaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return self._handle_ingreso(serializer.validated_data["placa"])


class ControlSalidaVehicularView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "control_salida"
    serializer_class = ControlAccesoResponseSerializer  # Para documentación

    def _handle_salida(self, placa):
        try:
            vehiculo = Vehiculo.objects.get(placa__iexact=placa)
        except Vehiculo.DoesNotExist:
            return Response({"detail": "Vehículo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if vehiculo.propiedad:
            return Response({"detail": "Salida de residente registrada."}, status=status.HTTP_200_OK)

        visita = Visita.objects.filter(
            visitante__vehiculos=vehiculo,
            ingreso_real__isnull=False,
            salida_real__isnull=True
        ).order_by("-ingreso_real").first()

        if not visita:
            return Response({"detail": "No se encontró una visita activa para este vehículo."}, status=status.HTTP_404_NOT_FOUND)
        
        visita.salida_real = timezone.now()
        visita.save()
        return Response({"detail": "Salida registrada con éxito."}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ConsultaPlacaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return self._handle_salida(serializer.validated_data["placa"])


class VisitasAbiertasView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):
        visitas_abiertas = Visita.objects.filter(ingreso_real__isnull=False, salida_real__isnull=True)
        serializer = VisitaSerializer(visitas_abiertas, many=True)
        return Response(serializer.data)


class ExportVisitasCSVView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = SimpleOperationResponseSerializer  # Para documentación
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="visitas.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Visitante', 'Documento', 'Propiedad', 'Ingreso Real', 'Salida Programada'])
        visitas = Visita.objects.select_related('visitante', 'propiedad').all()
        for v in visitas:
            writer.writerow([v.id, v.visitante.nombre_completo, v.visitante.documento, v.propiedad.numero_casa, v.ingreso_real, v.fecha_salida_programada])
        return response


class CerrarVisitasVencidasView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = SimpleOperationResponseSerializer  # Para documentación
    def post(self, request, *args, **kwargs):
        from django.core.management import call_command
        call_command('cerrar_visitas_vencidas')
        return Response({"detail": "Comando para cerrar visitas vencidas ejecutado."}, status=status.HTTP_200_OK)


class DashboardResumenView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = DashboardResumenResponseSerializer  # Para documentación
    def get(self, request, *args, **kwargs):
        abiertas = Visita.objects.filter(ingreso_real__isnull=False, salida_real__isnull=True).count()
        total_hoy = Visita.objects.filter(ingreso_real__date=timezone.now().date()).count()
        return Response({"visitas_abiertas": abiertas, "total_ingresos_hoy": total_hoy})


class DashboardSeriesView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = DashboardSeriesResponseSerializer  # Para documentación
    def get(self, request, *args, **kwargs):
        return Response({"series": "data"})


class DashboardTopVisitantesView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = TopVisitantesResponseSerializer  # Para documentación
    def get(self, request, *args, **kwargs):
        days = int(request.query_params.get('days', 30))
        limit = int(request.query_params.get('limit', 5))
        since = timezone.now() - timedelta(days=days)
        top_visitantes = Visita.objects.filter(ingreso_real__gte=since).values('visitante__nombre_completo').annotate(count=Count('id')).order_by('-count')[:limit]
        return Response({"items": list(top_visitantes)})


class IAControlVehicularView(APIView):
    permission_classes = [HasAPIKey]
    serializer_class = ControlAccesoResponseSerializer  # Para documentación
    
    def _registrar_evento(self, tipo_evento, placa, accion, motivo, vehiculo=None):
        """Registra el evento en la base de datos"""
        return EventoSeguridad.objects.create(
            tipo_evento=tipo_evento, 
            placa_detectada=placa, 
            accion=accion, 
            motivo=motivo, 
            vehiculo_registrado=vehiculo
        )

    def post(self, request, *args, **kwargs):
        """
        Endpoint para control vehicular por IA
        Recibe: {"placa": "ABC123", "tipo": "INGRESO"}
        Responde con información detallada del acceso
        """
        placa = request.data.get('placa', '').strip().upper()
        tipo_evento = request.data.get('tipo', 'INGRESO').upper()
        timestamp = timezone.now()

        # Validaciones
        if not placa:
            return Response({
                "error": "El campo 'placa' es requerido.",
                "timestamp": timestamp.isoformat(),
                "accion": "DENEGADO"
            }, status=status.HTTP_400_BAD_REQUEST)

        if tipo_evento not in ['INGRESO', 'SALIDA']:
            return Response({
                "error": "El campo 'tipo' debe ser 'INGRESO' o 'SALIDA'.",
                "timestamp": timestamp.isoformat(),
                "accion": "DENEGADO"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Buscar vehículo en la base de datos
        vehiculo = Vehiculo.objects.filter(placa__iexact=placa).first()
        
        # Determinar información del vehículo
        vehiculo_info = None
        acceso_permitido = False
        motivo = ""
        status_code = status.HTTP_403_FORBIDDEN
        
        if vehiculo:
            if vehiculo.propiedad:
                # Vehículo de residente - siempre permitido
                vehiculo_info = {
                    "tipo": "RESIDENTE",
                    "propiedad": vehiculo.propiedad.numero_casa,
                    "propiedad_id": vehiculo.propiedad.id,
                    "autorizado": True
                }
                acceso_permitido = True
                motivo = f"Vehículo autorizado para {vehiculo.propiedad.numero_casa}"
                status_code = status.HTTP_200_OK
                
            elif vehiculo.visitante:
                # Vehículo de visitante - revisar visitas vigentes
                visita_vigente = Visita.objects.filter(
                    visitante=vehiculo.visitante,
                    ingreso_real__isnull=True,
                    fecha_ingreso_programado__lte=timestamp,
                    fecha_salida_programada__gte=timestamp
                ).first()
                
                if visita_vigente:
                    vehiculo_info = {
                        "tipo": "VISITANTE", 
                        "visitante": vehiculo.visitante.nombre_completo,
                        "propiedad": visita_vigente.propiedad.numero_casa,
                        "autorizado": True
                    }
                    acceso_permitido = True
                    motivo = f"Visitante autorizado para {visita_vigente.propiedad.numero_casa}"
                    status_code = status.HTTP_200_OK
                    
                    # Marcar ingreso real si es INGRESO
                    if tipo_evento == 'INGRESO':
                        visita_vigente.ingreso_real = timestamp
                        visita_vigente.save()
                else:
                    vehiculo_info = {
                        "tipo": "VISITANTE",
                        "visitante": vehiculo.visitante.nombre_completo,
                        "autorizado": False
                    }
                    motivo = "Visitante sin visita programada vigente"
                    
            else:
                # Vehículo registrado pero sin asignar
                vehiculo_info = {
                    "tipo": "SIN_ASIGNAR",
                    "autorizado": False
                }
                motivo = f"Vehículo {placa} registrado pero sin autorización específica"
        else:
            # Vehículo no registrado
            vehiculo_info = {
                "tipo": "NO_REGISTRADO",
                "autorizado": False
            }
            motivo = f"Placa '{placa}' no encontrada en el sistema"

        # Determinar acción para el registro
        accion = EventoSeguridad.AccionTomada.PERMITIDO if acceso_permitido else EventoSeguridad.AccionTomada.DENEGADO

        # Registrar evento
        evento = self._registrar_evento(tipo_evento, placa, accion, motivo, vehiculo)

        # Preparar respuesta detallada
        response_data = {
            "evento_id": evento.id,
            "timestamp": timestamp.isoformat(),
            "placa": placa,
            "tipo_evento": tipo_evento,
            "accion": accion,
            "acceso_permitido": acceso_permitido,
            "motivo": motivo,
            "vehiculo": vehiculo_info,
            "mensaje": f"{'✅ Acceso permitido' if acceso_permitido else '❌ Acceso denegado'} para {placa}"
        }

        # Notificar si es necesario (para auditoría)
        try:
            if vehiculo and vehiculo.propiedad:
                notificar_acceso_vehicular(
                    usuario_accion=None,  # Sistema IA
                    ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                    placa=placa,
                    propiedad_id=vehiculo.propiedad.id,
                    permitido=acceso_permitido
                )
        except Exception as e:
            # No fallar si la notificación falla
            print(f"Warning: Error en notificación: {e}")

        # Devolver respuesta con el código de estado apropiado
        return Response(response_data, status=status_code)


class IAProcesarImagenView(APIView):
    """
    Endpoint para procesar imágenes con IA
    Compatible con el frontend React
    """
    permission_classes = [HasAPIKey]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        """
        Procesa imagen para reconocimiento de placas
        Acepta: imagen, image, file como nombres de campo
        """
        # Buscar la imagen en diferentes nombres de campo
        imagen = None
        for field_name in ['imagen', 'image', 'file']:
            if field_name in request.FILES:
                imagen = request.FILES[field_name]
                break
        
        if not imagen:
            return Response({
                "error": "No se recibió ninguna imagen",
                "campos_esperados": ["imagen", "image", "file"],
                "timestamp": timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Simular procesamiento de IA (placeholder)
        # En un entorno real, aquí iría el procesamiento con OpenCV/TensorFlow
        timestamp = timezone.now()
        placa_detectada = "DEBUG-VIDEO-001"  # Placa simulada
        
        # Usar la misma lógica que IAControlVehicularView
        vehiculo = Vehiculo.objects.filter(placa__iexact=placa_detectada).first()
        
        if vehiculo:
            acceso_permitido = True
            motivo = f"Placa {placa_detectada} encontrada en el sistema"
            accion = "PERMITIDO"
            status_code = status.HTTP_200_OK
        else:
            acceso_permitido = False
            motivo = f"Placa '{placa_detectada}' no encontrada en el sistema"
            accion = "DENEGADO"
            status_code = status.HTTP_403_FORBIDDEN
        
        # Registrar evento
        evento = EventoSeguridad.objects.create(
            tipo_evento="INGRESO",
            placa_detectada=placa_detectada,
            accion=accion,
            motivo=motivo,
            vehiculo_registrado=vehiculo
        )
        
        response_data = {
            "evento_id": evento.id,
            "timestamp": timestamp.isoformat(),
            "placa": placa_detectada,
            "tipo_evento": "INGRESO",
            "accion": accion,
            "acceso_permitido": acceso_permitido,
            "motivo": motivo,
            "vehiculo": {
                "tipo": "REGISTRADO" if vehiculo else "NO_REGISTRADO",
                "autorizado": acceso_permitido
            },
            "mensaje": f"{'✅ Acceso permitido' if acceso_permitido else '❌ Acceso denegado'} para {placa_detectada}",
            "imagen_procesada": True,
            "imagen_size": len(imagen.read()) if hasattr(imagen, 'read') else 0
        }
        
        return Response(response_data, status=status_code)

class GateDashboardView(APIView):
    """
    Endpoint para el dashboard del gate
    Proporciona información en tiempo real para la interfaz web
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtiene el estado actual del sistema de gate"""
        from django.db.models import Count
        from datetime import timedelta
        
        ahora = timezone.now()
        hoy = ahora.date()
        ayer = hoy - timedelta(days=1)
        
        # Estadísticas de hoy
        eventos_hoy = EventoSeguridad.objects.filter(fecha_hora__date=hoy)
        eventos_permitidos_hoy = eventos_hoy.filter(accion='PERMITIDO').count()
        eventos_denegados_hoy = eventos_hoy.filter(accion='DENEGADO').count()
        
        # Últimos eventos (últimos 10)
        ultimos_eventos = EventoSeguridad.objects.select_related('vehiculo_registrado', 'vehiculo_registrado__propiedad').order_by('-fecha_hora')[:10]
        
        eventos_data = []
        for evento in ultimos_eventos:
            vehiculo_info = "No registrado"
            if evento.vehiculo_registrado:
                if evento.vehiculo_registrado.propiedad:
                    vehiculo_info = f"Residente - {evento.vehiculo_registrado.propiedad.numero_casa}"
                elif evento.vehiculo_registrado.visitante:
                    vehiculo_info = f"Visitante - {evento.vehiculo_registrado.visitante.nombre_completo}"
                else:
                    vehiculo_info = "Vehículo sin asignar"
            
            eventos_data.append({
                "id": evento.id,
                "timestamp": evento.fecha_hora.isoformat(),
                "placa": evento.placa_detectada,
                "tipo_evento": evento.tipo_evento,
                "accion": evento.accion,
                "motivo": evento.motivo,
                "vehiculo_info": vehiculo_info,
                "tiempo_relativo": self._tiempo_relativo(evento.fecha_hora, ahora)
            })
        
        # Estadísticas por placas más frecuentes
        placas_frecuentes = (EventoSeguridad.objects
                           .filter(fecha_hora__date=hoy)
                           .values('placa_detectada')
                           .annotate(total=Count('id'))
                           .order_by('-total')[:5])
        
        # Vehículos registrados
        total_vehiculos = Vehiculo.objects.count()
        vehiculos_residentes = Vehiculo.objects.filter(propiedad__isnull=False).count()
        vehiculos_visitantes = Vehiculo.objects.filter(visitante__isnull=False).count()
        
        response_data = {
            "timestamp": ahora.isoformat(),
            "estadisticas_hoy": {
                "total_eventos": eventos_hoy.count(),
                "accesos_permitidos": eventos_permitidos_hoy,
                "accesos_denegados": eventos_denegados_hoy,
                "porcentaje_exito": round((eventos_permitidos_hoy / max(eventos_hoy.count(), 1)) * 100, 2)
            },
            "vehiculos_registrados": {
                "total": total_vehiculos,
                "residentes": vehiculos_residentes,
                "visitantes": vehiculos_visitantes,
                "sin_asignar": total_vehiculos - vehiculos_residentes - vehiculos_visitantes
            },
            "ultimos_eventos": eventos_data,
            "placas_frecuentes_hoy": list(placas_frecuentes),
            "sistema": {
                "estado": "ACTIVO",
                "version": "1.0.0",
                "modo": "SIMULACION" if 'test_video' in str(request.path) else "PRODUCCION"
            }
        }
        
        return Response(response_data)
    
    def _tiempo_relativo(self, fecha_evento, ahora):
        """Convierte timestamp a tiempo relativo legible"""
        diff = ahora - fecha_evento
        
        if diff.total_seconds() < 60:
            return f"Hace {int(diff.total_seconds())} segundos"
        elif diff.total_seconds() < 3600:
            return f"Hace {int(diff.total_seconds() / 60)} minutos"
        elif diff.total_seconds() < 86400:
            return f"Hace {int(diff.total_seconds() / 3600)} horas"
        else:
            return f"Hace {diff.days} días"

class VerificarRostroView(APIView):
    permission_classes = [HasAPIKey]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = SimpleOperationResponseSerializer  # Para documentación

    def post(self, request, *args, **kwargs):
        if 'foto' not in request.FILES:
            return Response({"error": "No se ha proporcionado ninguna foto."}, status=status.HTTP_400_BAD_REQUEST)
        
        foto = request.FILES['foto']
        image_bytes = foto.read()

        try:
            rekognition_client = boto3.client('rekognition')
            collection_id = settings.AWS_REKOGNITION_COLLECTION_ID
        except Exception as e:
            return Response({"error": f"Error de configuración de AWS: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response = rekognition_client.search_faces_by_image(
                CollectionId=collection_id, Image={'Bytes': image_bytes}, MaxFaces=1, FaceMatchThreshold=85
            )
            if not response['FaceMatches']:
                return Response({"detail": "Acceso denegado. Rostro no reconocido."}, status=status.HTTP_403_FORBIDDEN)
            
            face_match = response['FaceMatches'][0]
            face_id = face_match['Face']['FaceId']
            
            try:
                residente = Residente.objects.get(face_id_aws=face_id)
                return Response({
                    "detail": f"Acceso permitido para {residente.usuario.get_full_name()}.",
                    "residente_id": residente.id,
                    "confianza": f"{face_match['Similarity']:.2f}%"
                }, status=status.HTTP_200_OK)
            except Residente.DoesNotExist:
                return Response({"detail": "Acceso denegado. Rostro no sincronizado."}, status=status.HTTP_403_FORBIDDEN)
        
        except rekognition_client.exceptions.InvalidParameterException:
            return Response({"error": "No se detectó un rostro en la imagen enviada."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error al procesar la imagen con AWS: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeteccionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeteccionSerializer
    
    def get_queryset(self):
        qs = Deteccion.objects.all()
        cam = self.request.query_params.get("camera")
        if cam:
            qs = qs.filter(camera__name=cam)
        return qs

# --- ViewSets para el Router (CRUDs estándar) ---

class VisitaViewSet(viewsets.ModelViewSet):
    serializer_class = VisitaSerializer
    # Filtros avanzados
    filterset_fields = {
        'propiedad': ['exact'],
        'visitante': ['exact'],
        'fecha_ingreso_programado': ['gte', 'lte', 'exact'],
        'fecha_salida_programada': ['gte', 'lte', 'exact'],
        'ingreso_real': ['isnull'],
        'salida_real': ['isnull'],
        'estado': ['exact'],
    }
    search_fields = ['visitante__nombre_completo', 'visitante__documento', 'propiedad__numero']
    ordering_fields = ['fecha_ingreso_programado', 'fecha_salida_programada', 'ingreso_real']
    ordering = ['-fecha_ingreso_programado']

    def get_queryset(self):
        """
        Filtra las visitas según el rol del usuario:
        - PROPIETARIO: Ve todas las visitas del condominio
        - SEGURIDAD: Ve todas las visitas (necesario para control de acceso)
        - RESIDENTE: Solo ve visitas a propiedades donde es residente
        """
        user = self.request.user
        
        try:
            if user.profile.role in ['PROPIETARIO', 'SEGURIDAD']:
                # Propietarios y personal de seguridad ven todas las visitas
                return Visita.objects.select_related('visitante', 'propiedad').all()
            else:
                # Residentes ven solo visitas a sus propiedades
                from usuarios.models import Residente
                try:
                    residente = Residente.objects.get(usuario=user)
                    if residente.propiedad:
                        return Visita.objects.select_related('visitante', 'propiedad').filter(
                            propiedad=residente.propiedad
                        )
                    else:
                        return Visita.objects.none()
                except Residente.DoesNotExist:
                    return Visita.objects.none()
        except:
            return Visita.objects.none()

    def get_permissions(self):
        # Solo propietarios pueden crear, actualizar o eliminar visitas
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsPropietario]
        # Personal de seguridad y propietarios pueden ver visitas
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

class VehiculoViewSet(viewsets.ModelViewSet):
    serializer_class = VehiculoSerializer
    # Filtros avanzados - solo campos que existen en el modelo
    filterset_fields = {
        'placa': ['exact', 'icontains'],
        'propiedad': ['exact'],
        'visitante': ['exact'],
    }
    search_fields = ['placa', 'propiedad__numero_casa']
    ordering_fields = ['placa']
    ordering = ['placa']

    def get_queryset(self):
        """
        Filtra los vehículos según el rol del usuario:
        - PROPIETARIO: Ve todos los vehículos del condominio
        - SEGURIDAD: Ve todos los vehículos (necesario para control de acceso)
        - RESIDENTE: Solo ve vehículos de propiedades donde es residente
        """
        user = self.request.user
        
        try:
            if user.profile.role in ['PROPIETARIO', 'SEGURIDAD']:
                # Propietarios y personal de seguridad ven todos los vehículos
                return Vehiculo.objects.select_related('propiedad').all()
            else:
                # Residentes ven solo vehículos de sus propiedades
                from usuarios.models import Residente
                try:
                    residente = Residente.objects.get(usuario=user)
                    if residente.propiedad:
                        return Vehiculo.objects.select_related('propiedad').filter(
                            propiedad=residente.propiedad
                        )
                    else:
                        return Vehiculo.objects.none()
                except Residente.DoesNotExist:
                    return Vehiculo.objects.none()
        except:
            return Vehiculo.objects.none()

    def get_permissions(self):
        # Solo propietarios pueden crear, actualizar o eliminar vehículos
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsPropietario]
        # Personal de seguridad y propietarios pueden ver vehículos
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer
    # Filtros avanzados - CORREGIDOS para coincidir con el modelo real
    filterset_fields = {
        'nombre_completo': ['icontains'],  # Campo correcto del modelo
        'documento': ['exact'],  # Campo correcto del modelo
        'telefono': ['exact', 'icontains'],
        'email': ['icontains'],  # Campo adicional que existe
    }
    search_fields = ['nombre_completo', 'documento', 'telefono']  # Campos correctos
    ordering_fields = ['nombre_completo', 'documento']  # Campos correctos
    ordering = ['nombre_completo']

    def get_permissions(self):
        # Solo propietarios pueden crear, actualizar o eliminar visitantes
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsPropietario]
        # Personal de seguridad y propietarios pueden ver visitantes
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Registra el visitante y notifica a propietarios de la propiedad visitada"""
        visitante_data = serializer.validated_data
        nombre_completo = visitante_data.get('nombre_completo', '')
        propiedad_visitada = visitante_data.get('propiedad_visitada')
        
        # Guardar el visitante
        visitante = serializer.save()
        
        # Sistema nuevo: notificar a usuarios relacionados con la propiedad
        if propiedad_visitada:
            notificar_visitante_registrado(
                usuario_accion=self.request.user,
                ip_address=getattr(self.request, 'ip_address', None),
                propiedad_id=propiedad_visitada.id,
                nombre_visitante=nombre_completo
            )

class EventoSeguridadViewSet(viewsets.ModelViewSet):
    queryset = EventoSeguridad.objects.all()
    serializer_class = EventoSeguridadSerializer
    # Filtros avanzados - CORREGIDOS para coincidir con el modelo real
    filterset_fields = {
        'tipo_evento': ['exact'],  # Campo correcto del modelo
        'fecha_hora': ['gte', 'lte', 'exact'],
        'accion': ['exact'],  # Campo que existe en el modelo
        'placa_detectada': ['icontains'],  # Campo que existe en el modelo
        'vehiculo_registrado': ['exact'],  # Relación que existe
    }
    search_fields = ['placa_detectada', 'motivo']  # Campos que existen
    ordering_fields = ['fecha_hora', 'tipo_evento', 'accion']  # Campos que existen
    ordering = ['-fecha_hora']

    def get_permissions(self):
        # Solo personal de seguridad puede crear, actualizar o eliminar eventos
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsPersonalSeguridad]
        # Cualquier usuario autenticado puede ver eventos de seguridad
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    permission_classes = [IsAuthenticated]