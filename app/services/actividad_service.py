# -*- coding: utf-8 -*-
"""
Servicio para la lógica de negocio de actividades.
"""

from datetime import datetime, date
from collections import OrderedDict


class ActividadService:
    """Servicio para manejar la lógica de negocio relacionada con actividades."""
    
    def __init__(self, database_service=None):
        """Inicializar el servicio de actividades."""
        self.db_service = database_service
        self.db = None
        self.Actividad = None
        self.Viaje = None
        
    def init_models(self, models_dict, database_instance):
        """Inicializar los modelos necesarios."""
        self.Actividad = models_dict['Actividad']
        self.Viaje = models_dict['Viaje']
        self.db = database_instance
        
    def crear_actividad(self, viaje_id, nombre, fecha, destino='general', hora=None, ubicacion='', descripcion=''):
        """
        Crear una nueva actividad para un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            nombre (str): Nombre de la actividad
            fecha (str|date): Fecha de la actividad
            destino (str): Destino/ciudad de la actividad (default: 'general')
            hora (str|time): Hora de la actividad (optional)
            ubicacion (str): Ubicación específica (optional)
            descripcion (str): Descripción de la actividad (optional)
            
        Returns:
            dict: Resultado con success y actividad_id
        """
        try:
            # Convertir fecha si es string
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            
            # Convertir hora si es string no vacío
            if hora and isinstance(hora, str) and hora.strip():
                hora = datetime.strptime(hora, '%H:%M').time()
            else:
                hora = None  # Si está vacío o es None, usar None
            
            # Crear la actividad
            actividad = self.Actividad(
                viaje_id=viaje_id,
                destino=destino,
                nombre=nombre,
                fecha=fecha,
                hora=hora,
                ubicacion=ubicacion,
                descripcion=descripcion,
                completada=False  # Por defecto no completada
            )
            
            self.db.session.add(actividad)
            self.db.session.commit()
            
            return {'success': True, 'actividad_id': actividad.id}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def completar_actividad(self, actividad_id, completada=None):
        """
        Marcar una actividad como completada o no completada.
        
        Args:
            actividad_id (int): ID de la actividad
            completada (bool): Estado de completado (None para toggle)
            
        Returns:
            dict: Resultado con success y estado actual
        """
        try:
            actividad = self.Actividad.query.get(actividad_id)
            if not actividad:
                return {'success': False, 'error': 'Actividad no encontrada'}
            
            # Si no se especifica completada, hacer toggle
            if completada is None:
                actividad.completada = not actividad.completada
            else:
                actividad.completada = completada
            
            self.db.session.commit()
            
            return {'success': True, 'completada': actividad.completada}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def obtener_actividades_por_viaje(self, viaje_id, solo_pendientes=False):
        """
        Obtener todas las actividades de un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            solo_pendientes (bool): Solo actividades no completadas
            
        Returns:
            list: Lista de actividades del viaje
        """
        query = self.Actividad.query.filter_by(viaje_id=viaje_id)
        
        if solo_pendientes:
            query = query.filter_by(completada=False)
        
        return query.order_by(self.Actividad.fecha, self.Actividad.hora).all()
    
    def agrupar_actividades_por_destino(self, viaje_id):
        """
        Agrupa y ordena las actividades de un viaje por destino y fecha/hora.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            OrderedDict: Actividades agrupadas por destino y ordenadas
        """
        actividades = self.obtener_actividades_por_viaje(viaje_id)
        actividades_agrupadas = {}
        
        # Agrupar actividades por destino
        for actividad in actividades:
            destino = actividad.destino or 'general'
            if destino not in actividades_agrupadas:
                actividades_agrupadas[destino] = []
            actividades_agrupadas[destino].append(actividad)
        
        # Ordenar actividades dentro de cada destino por fecha y hora
        for destino in actividades_agrupadas:
            actividades_agrupadas[destino].sort(key=lambda a: (
                a.fecha,
                a.hora if a.hora else datetime.min.time()
            ))
        
        # Crear diccionario ordenado: 'general' primero, luego resto alfabéticamente
        actividades_ordenadas = OrderedDict()
        
        # Primero 'general' si existe
        if 'general' in actividades_agrupadas:
            actividades_ordenadas['general'] = actividades_agrupadas['general']
        
        # Luego el resto ordenado alfabéticamente
        for destino in sorted(actividades_agrupadas.keys()):
            if destino != 'general':
                actividades_ordenadas[destino] = actividades_agrupadas[destino]
        
        return actividades_ordenadas
    
    def obtener_actividades_por_fecha(self, viaje_id, fecha):
        """
        Obtener actividades de un viaje para una fecha específica.
        
        Args:
            viaje_id (int): ID del viaje
            fecha (date|str): Fecha para filtrar
            
        Returns:
            list: Lista de actividades para esa fecha
        """
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        return self.Actividad.query.filter_by(
            viaje_id=viaje_id,
            fecha=fecha
        ).order_by(self.Actividad.hora).all()
    
    def obtener_estadisticas_actividades(self, viaje_id):
        """
        Calcular estadísticas de actividades para un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Estadísticas de actividades
        """
        actividades = self.obtener_actividades_por_viaje(viaje_id)
        total = len(actividades)
        completadas = sum(1 for a in actividades if a.completada)
        pendientes = total - completadas
        
        # Calcular porcentaje de completado
        porcentaje_completado = (completadas / total * 100) if total > 0 else 0
        
        # Agrupar por destino
        destinos = {}
        for actividad in actividades:
            destino = actividad.destino or 'general'
            if destino not in destinos:
                destinos[destino] = {'total': 0, 'completadas': 0}
            destinos[destino]['total'] += 1
            if actividad.completada:
                destinos[destino]['completadas'] += 1
        
        return {
            'total': total,
            'completadas': completadas,
            'pendientes': pendientes,
            'porcentaje_completado': round(porcentaje_completado, 1),
            'por_destino': destinos
        }
    
    def eliminar_actividad(self, actividad_id):
        """
        Eliminar una actividad.
        
        Args:
            actividad_id (int): ID de la actividad a eliminar
            
        Returns:
            dict: Resultado con success
        """
        try:
            actividad = self.Actividad.query.get(actividad_id)
            if not actividad:
                return {'success': False, 'error': 'Actividad no encontrada'}
            
            self.db.session.delete(actividad)
            self.db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def actualizar_actividad(self, actividad_id, **kwargs):
        """
        Actualizar campos de una actividad.
        
        Args:
            actividad_id (int): ID de la actividad
            **kwargs: Campos a actualizar
            
        Returns:
            dict: Resultado con success
        """
        try:
            actividad = self.Actividad.query.get(actividad_id)
            if not actividad:
                return {'success': False, 'error': 'Actividad no encontrada'}
            
            # Actualizar campos permitidos
            campos_permitidos = ['nombre', 'fecha', 'hora', 'ubicacion', 'descripcion', 'destino', 'completada']
            
            for campo, valor in kwargs.items():
                if campo in campos_permitidos and hasattr(actividad, campo):
                    # Conversiones especiales
                    if campo == 'fecha' and isinstance(valor, str):
                        valor = datetime.strptime(valor, '%Y-%m-%d').date()
                    elif campo == 'hora' and isinstance(valor, str):
                        valor = datetime.strptime(valor, '%H:%M').time() if valor else None
                    
                    setattr(actividad, campo, valor)
            
            self.db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}


# Instancia global del servicio
actividad_service = ActividadService()
