# Archivo: auditoria/eventos.py
# Sistema de eventos y notificaciones automáticas

from typing import List, Dict, Any
from django.contrib.auth.models import User
from .services import registrar_evento
from notificaciones.services import notificar_usuario

class EventoNotificador:
    """
    Clase para registrar eventos de auditoría y enviar notificaciones automáticas
    a usuarios relacionados según el tipo de evento.
    """
    
    @staticmethod
    def obtener_usuarios_relacionados_propiedad(propiedad_id: int) -> List[User]:
        """
        Obtiene todos los usuarios relacionados con una propiedad:
        - Propietario
        - Residentes de la propiedad
        """
        from condominio.models import Propiedad
        from usuarios.models import Residente
        
        usuarios_relacionados = []
        
        try:
            propiedad = Propiedad.objects.get(id=propiedad_id)
            
            # Propietario principal
            if propiedad.propietario:
                usuarios_relacionados.append(propiedad.propietario)
            
            # Residentes asociados a la propiedad
            residentes = Residente.objects.filter(propiedad=propiedad)
            for residente in residentes:
                if residente.user and residente.user not in usuarios_relacionados:
                    usuarios_relacionados.append(residente.user)
                    
        except Propiedad.DoesNotExist:
            pass
            
        return usuarios_relacionados
    
    @staticmethod
    def notificar_evento_financiero(evento_tipo: str, usuario_accion: User, ip_address: str, 
                                  propiedad_id: int, detalles: Dict[str, Any]):
        """
        Registra evento financiero y notifica a usuarios relacionados
        """
        # Registrar en auditoría
        descripcion = f"Evento financiero: {evento_tipo}. Detalles: {detalles}"
        registrar_evento(
            usuario=usuario_accion,
            ip_address=ip_address,
            accion=f"Evento Financiero: {evento_tipo}",
            descripcion=descripcion
        )
        
        # Obtener usuarios a notificar
        usuarios_relacionados = EventoNotificador.obtener_usuarios_relacionados_propiedad(propiedad_id)
        
        # Preparar notificación según tipo de evento
        titulo, mensaje = EventoNotificador._generar_mensaje_financiero(evento_tipo, detalles)
        
        # Enviar notificaciones
        for usuario in usuarios_relacionados:
            notificar_usuario(
                user=usuario,
                title=titulo,
                body=mensaje,
                data={
                    "tipo_evento": evento_tipo,
                    "propiedad_id": propiedad_id,
                    "detalles": detalles
                }
            )
    
    @staticmethod
    def notificar_evento_seguridad(evento_tipo: str, usuario_accion: User, ip_address: str,
                                 propiedad_id: int = None, detalles: Dict[str, Any] = None):
        """
        Registra evento de seguridad y notifica según corresponda
        """
        # Registrar en auditoría
        descripcion = f"Evento de seguridad: {evento_tipo}. Detalles: {detalles or {}}"
        registrar_evento(
            usuario=usuario_accion,
            ip_address=ip_address,
            accion=f"Evento Seguridad: {evento_tipo}",
            descripcion=descripcion
        )
        
        # Notificar según tipo de evento
        if evento_tipo in ["VISITANTE_REGISTRADO", "ACCESO_VEHICULAR"] and propiedad_id:
            usuarios_relacionados = EventoNotificador.obtener_usuarios_relacionados_propiedad(propiedad_id)
            titulo, mensaje = EventoNotificador._generar_mensaje_seguridad(evento_tipo, detalles)
            
            for usuario in usuarios_relacionados:
                notificar_usuario(
                    user=usuario,
                    title=titulo,
                    body=mensaje,
                    data={
                        "tipo_evento": evento_tipo,
                        "propiedad_id": propiedad_id,
                        "detalles": detalles or {}
                    }
                )
        elif evento_tipo in ["ALARMA_GENERAL", "INCIDENTE_CONDOMINIO"]:
            # Notificar a todos los usuarios del condominio
            EventoNotificador._notificar_todos_usuarios(evento_tipo, detalles)
    
    @staticmethod
    def notificar_evento_mantenimiento(evento_tipo: str, usuario_accion: User, ip_address: str,
                                     propiedad_id: int = None, detalles: Dict[str, Any] = None):
        """
        Registra evento de mantenimiento y notifica según corresponda
        """
        # Registrar en auditoría
        descripcion = f"Evento de mantenimiento: {evento_tipo}. Detalles: {detalles or {}}"
        registrar_evento(
            usuario=usuario_accion,
            ip_address=ip_address,
            accion=f"Evento Mantenimiento: {evento_tipo}",
            descripcion=descripcion
        )
        
        # Notificar según tipo y si afecta propiedad específica
        if propiedad_id:
            usuarios_relacionados = EventoNotificador.obtener_usuarios_relacionados_propiedad(propiedad_id)
            titulo, mensaje = EventoNotificador._generar_mensaje_mantenimiento(evento_tipo, detalles)
            
            for usuario in usuarios_relacionados:
                notificar_usuario(
                    user=usuario,
                    title=titulo,
                    body=mensaje,
                    data={
                        "tipo_evento": evento_tipo,
                        "propiedad_id": propiedad_id,
                        "detalles": detalles or {}
                    }
                )
    
    @staticmethod
    def _generar_mensaje_financiero(evento_tipo: str, detalles: Dict[str, Any]) -> tuple:
        """Genera título y mensaje para eventos financieros"""
        mensajes = {
            "MULTA_ASIGNADA": (
                "💰 Nueva Multa Asignada",
                f"Se ha asignado una multa por ${detalles.get('monto', 'N/A')}. Concepto: {detalles.get('concepto', 'N/A')}"
            ),
            "GASTO_ASIGNADO": (
                "📋 Nuevo Gasto Asignado", 
                f"Se ha asignado un gasto por ${detalles.get('monto', 'N/A')}. Descripción: {detalles.get('descripcion', 'N/A')}"
            ),
            "PAGO_RECIBIDO": (
                "✅ Pago Recibido",
                f"Se ha recibido su pago por ${detalles.get('monto', 'N/A')}. ¡Gracias!"
            ),
            "RESERVA_CONFIRMADA": (
                "🎯 Reserva Confirmada",
                f"Su reserva para {detalles.get('area_comun', 'N/A')} ha sido confirmada"
            )
        }
        return mensajes.get(evento_tipo, ("📢 Evento Financiero", "Se ha registrado un evento financiero"))
    
    @staticmethod
    def _generar_mensaje_seguridad(evento_tipo: str, detalles: Dict[str, Any]) -> tuple:
        """Genera título y mensaje para eventos de seguridad"""
        mensajes = {
            "VISITANTE_REGISTRADO": (
                "👤 Visitante Registrado",
                f"Se ha registrado una visita: {detalles.get('nombre', 'N/A')}"
            ),
            "ACCESO_VEHICULAR": (
                "🚗 Acceso Vehicular",
                f"Vehículo placa {detalles.get('placa', 'N/A')} - {detalles.get('accion', 'N/A')}"
            ),
            "ALARMA_GENERAL": (
                "🚨 Alerta General",
                f"Alerta en el condominio: {detalles.get('motivo', 'N/A')}"
            )
        }
        return mensajes.get(evento_tipo, ("🔒 Evento Seguridad", "Se ha registrado un evento de seguridad"))
    
    @staticmethod
    def _generar_mensaje_mantenimiento(evento_tipo: str, detalles: Dict[str, Any]) -> tuple:
        """Genera título y mensaje para eventos de mantenimiento"""
        mensajes = {
            "SOLICITUD_CREADA": (
                "🔧 Nueva Solicitud Mantenimiento",
                f"Se ha creado una solicitud: {detalles.get('titulo', 'N/A')}"
            ),
            "SOLICITUD_ASIGNADA": (
                "👷 Mantenimiento Asignado",
                f"Su solicitud ha sido asignada a: {detalles.get('asignado_a', 'N/A')}"
            ),
            "SOLICITUD_COMPLETADA": (
                "✅ Mantenimiento Completado",
                f"Se ha completado el mantenimiento: {detalles.get('titulo', 'N/A')}"
            )
        }
        return mensajes.get(evento_tipo, ("🛠️ Evento Mantenimiento", "Se ha registrado un evento de mantenimiento"))
    
    @staticmethod
    def _notificar_todos_usuarios(evento_tipo: str, detalles: Dict[str, Any]):
        """Notifica a todos los usuarios del condominio"""
        usuarios = User.objects.filter(is_active=True)
        titulo, mensaje = EventoNotificador._generar_mensaje_seguridad(evento_tipo, detalles)
        
        for usuario in usuarios:
            notificar_usuario(
                user=usuario,
                title=titulo,
                body=mensaje,
                data={
                    "tipo_evento": evento_tipo,
                    "detalles": detalles or {}
                }
            )


# Funciones de conveniencia para usar en las vistas
def notificar_multa_asignada(usuario_accion: User, ip_address: str, propiedad_id: int, 
                           monto: str, concepto: str):
    """Notifica cuando se asigna una multa"""
    EventoNotificador.notificar_evento_financiero(
        evento_tipo="MULTA_ASIGNADA",
        usuario_accion=usuario_accion,
        ip_address=ip_address,
        propiedad_id=propiedad_id,
        detalles={"monto": monto, "concepto": concepto}
    )

def notificar_gasto_asignado(usuario_accion: User, ip_address: str, propiedad_id: int,
                           monto: str, descripcion: str):
    """Notifica cuando se asigna un gasto"""
    EventoNotificador.notificar_evento_financiero(
        evento_tipo="GASTO_ASIGNADO",
        usuario_accion=usuario_accion,
        ip_address=ip_address,
        propiedad_id=propiedad_id,
        detalles={"monto": monto, "descripcion": descripcion}
    )

def notificar_pago_recibido(usuario_accion: User, ip_address: str, propiedad_id: int, monto: str):
    """Notifica cuando se recibe un pago"""
    EventoNotificador.notificar_evento_financiero(
        evento_tipo="PAGO_RECIBIDO",
        usuario_accion=usuario_accion,
        ip_address=ip_address,
        propiedad_id=propiedad_id,
        detalles={"monto": monto}
    )

def notificar_visitante_registrado(usuario_accion: User, ip_address: str, propiedad_id: int, 
                                 nombre_visitante: str):
    """Notifica cuando se registra un visitante"""
    EventoNotificador.notificar_evento_seguridad(
        evento_tipo="VISITANTE_REGISTRADO",
        usuario_accion=usuario_accion,
        ip_address=ip_address,
        propiedad_id=propiedad_id,
        detalles={"nombre": nombre_visitante}
    )

def notificar_acceso_vehicular(usuario_accion: User, ip_address: str, propiedad_id: int,
                              placa: str, accion: str):
    """Notifica eventos de acceso vehicular"""
    EventoNotificador.notificar_evento_seguridad(
        evento_tipo="ACCESO_VEHICULAR",
        usuario_accion=usuario_accion,
        ip_address=ip_address,
        propiedad_id=propiedad_id,
        detalles={"placa": placa, "accion": accion}
    )