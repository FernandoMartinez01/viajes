# -*- coding: utf-8 -*-
"""
Servicio para la lógica de negocio de alojamientos de viaje.
"""

from datetime import datetime, date, timedelta
from collections import defaultdict, OrderedDict


class AlojamientoService:
    """Servicio para manejar la lógica de negocio relacionada con alojamientos."""
    
    def __init__(self, database_service=None):
        """Inicializar el servicio de alojamientos."""
        self.db_service = database_service
        self.db = None
        self.Alojamiento = None
        self.Viaje = None
        
    def init_models(self, models_dict, database_instance):
        """Inicializar los modelos necesarios."""
        self.Alojamiento = models_dict['Alojamiento']
        self.Viaje = models_dict['Viaje']
        self.db = database_instance
        
    def crear_alojamiento(self, viaje_id, nombre, destino, direccion, fecha_entrada, fecha_salida,
                         horario_checkin='15:00', horario_checkout='11:00', incluye_desayuno=False,
                         numero_confirmacion='', codigo_pin='', numero_checkin='', notas=''):
        """
        Crear un nuevo alojamiento para un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            nombre (str): Nombre del hotel/alojamiento
            destino (str): Ciudad/destino del alojamiento
            direccion (str): Dirección del alojamiento
            fecha_entrada (str|date): Fecha de check-in
            fecha_salida (str|date): Fecha de check-out
            horario_checkin (str|time): Hora de check-in (default: 15:00)
            horario_checkout (str|time): Hora de check-out (default: 11:00)
            incluye_desayuno (bool): Si incluye desayuno
            numero_confirmacion (str): Número de confirmación (optional)
            codigo_pin (str): Código PIN para acceso (optional)
            numero_checkin (str): Número de check-in online (optional)
            notas (str): Notas adicionales (optional)
            
        Returns:
            dict: Resultado con success y alojamiento_id
        """
        try:
            # Convertir fechas si son strings
            if isinstance(fecha_entrada, str):
                fecha_entrada = datetime.strptime(fecha_entrada, '%Y-%m-%d').date()
            if isinstance(fecha_salida, str):
                fecha_salida = datetime.strptime(fecha_salida, '%Y-%m-%d').date()
            
            # Convertir horarios si son strings
            if isinstance(horario_checkin, str):
                horario_checkin = datetime.strptime(horario_checkin, '%H:%M').time()
            if isinstance(horario_checkout, str):
                horario_checkout = datetime.strptime(horario_checkout, '%H:%M').time()
            
            # Validar fechas
            if fecha_salida <= fecha_entrada:
                return {'success': False, 'error': 'La fecha de salida debe ser posterior a la entrada'}
            
            # Crear el alojamiento
            alojamiento = self.Alojamiento(
                viaje_id=viaje_id,
                nombre=nombre,
                destino=destino,
                direccion=direccion,
                fecha_entrada=fecha_entrada,
                fecha_salida=fecha_salida,
                horario_checkin=horario_checkin,
                horario_checkout=horario_checkout,
                incluye_desayuno=incluye_desayuno,
                numero_confirmacion=numero_confirmacion,
                codigo_pin=codigo_pin,
                numero_checkin=numero_checkin,
                notas=notas
            )
            
            self.db.session.add(alojamiento)
            self.db.session.commit()
            
            return {'success': True, 'alojamiento_id': alojamiento.id}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def obtener_alojamientos_por_viaje(self, viaje_id):
        """
        Obtener todos los alojamientos de un viaje ordenados por fecha de entrada.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            list: Lista de alojamientos del viaje
        """
        return self.Alojamiento.query.filter_by(viaje_id=viaje_id).order_by(
            self.Alojamiento.fecha_entrada
        ).all()
    
    def agrupar_alojamientos_por_destino(self, viaje_id):
        """
        Agrupar alojamientos de un viaje por destino.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Diccionario con destinos como claves y listas de alojamientos como valores
        """
        alojamientos = self.obtener_alojamientos_por_viaje(viaje_id)
        alojamientos_agrupados = defaultdict(list)
        
        for alojamiento in alojamientos:
            destino_key = alojamiento.destino.lower() if alojamiento.destino else 'otros'
            alojamientos_agrupados[destino_key].append(alojamiento)
        
        # Convertir a OrderedDict y ordenar por número de alojamientos
        resultado = OrderedDict()
        destinos_ordenados = sorted(alojamientos_agrupados.items(), 
                                  key=lambda x: len(x[1]), reverse=True)
        
        for destino, alojamientos_lista in destinos_ordenados:
            resultado[destino] = sorted(alojamientos_lista, key=lambda x: x.fecha_entrada)
        
        return resultado
    
    def calcular_noches_estancia(self, viaje_id):
        """
        Calcular el total de noches de estancia del viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Información sobre noches de estancia
        """
        alojamientos = self.obtener_alojamientos_por_viaje(viaje_id)
        
        total_noches = 0
        estancias_por_destino = defaultdict(int)
        
        for alojamiento in alojamientos:
            noches = (alojamiento.fecha_salida - alojamiento.fecha_entrada).days
            total_noches += noches
            destino_key = alojamiento.destino.lower() if alojamiento.destino else 'otros'
            estancias_por_destino[destino_key] += noches
        
        return {
            'total_noches': total_noches,
            'total_alojamientos': len(alojamientos),
            'promedio_noches_por_alojamiento': round(total_noches / len(alojamientos), 1) if alojamientos else 0,
            'noches_por_destino': dict(estancias_por_destino)
        }
    
    def verificar_continuidad_alojamiento(self, viaje_id):
        """
        Verificar si hay gaps en la cobertura de alojamiento durante el viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Información sobre gaps y cobertura
        """
        alojamientos = self.obtener_alojamientos_por_viaje(viaje_id)
        
        if not alojamientos:
            return {'gaps': [], 'cobertura_completa': False, 'primer_alojamiento': None, 'ultimo_alojamiento': None}
        
        # Obtener fechas del viaje
        viaje = self.Viaje.query.get(viaje_id)
        if not viaje:
            return {'error': 'Viaje no encontrado'}
        
        gaps = []
        
        # Verificar gap antes del primer alojamiento
        primer_alojamiento = alojamientos[0]
        if primer_alojamiento.fecha_entrada > viaje.fecha_inicio:
            gap_dias = (primer_alojamiento.fecha_entrada - viaje.fecha_inicio).days
            if gap_dias > 0:
                gaps.append({
                    'tipo': 'inicio',
                    'fecha_inicio': viaje.fecha_inicio,
                    'fecha_fin': primer_alojamiento.fecha_entrada,
                    'dias': gap_dias,
                    'mensaje': f'Sin alojamiento los primeros {gap_dias} días del viaje'
                })
        
        # Verificar gaps entre alojamientos
        for i in range(len(alojamientos) - 1):
            actual = alojamientos[i]
            siguiente = alojamientos[i + 1]
            
            if actual.fecha_salida < siguiente.fecha_entrada:
                gap_dias = (siguiente.fecha_entrada - actual.fecha_salida).days
                gaps.append({
                    'tipo': 'intermedio',
                    'fecha_inicio': actual.fecha_salida,
                    'fecha_fin': siguiente.fecha_entrada,
                    'dias': gap_dias,
                    'alojamiento_anterior': actual.nombre,
                    'alojamiento_siguiente': siguiente.nombre,
                    'mensaje': f'Gap de {gap_dias} días entre {actual.nombre} y {siguiente.nombre}'
                })
        
        # Verificar gap después del último alojamiento
        ultimo_alojamiento = alojamientos[-1]
        if ultimo_alojamiento.fecha_salida < viaje.fecha_fin:
            gap_dias = (viaje.fecha_fin - ultimo_alojamiento.fecha_salida).days
            if gap_dias > 0:
                gaps.append({
                    'tipo': 'final',
                    'fecha_inicio': ultimo_alojamiento.fecha_salida,
                    'fecha_fin': viaje.fecha_fin,
                    'dias': gap_dias,
                    'mensaje': f'Sin alojamiento los últimos {gap_dias} días del viaje'
                })
        
        return {
            'gaps': gaps,
            'cobertura_completa': len(gaps) == 0,
            'primer_alojamiento': primer_alojamiento,
            'ultimo_alojamiento': ultimo_alojamiento,
            'total_gaps': len(gaps),
            'dias_sin_alojamiento': sum(gap['dias'] for gap in gaps)
        }
    
    def obtener_alojamientos_actuales(self, viaje_id):
        """
        Obtener alojamientos donde el usuario se encuentra actualmente.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            list: Lista de alojamientos actuales
        """
        hoy = date.today()
        
        return self.Alojamiento.query.filter(
            self.Alojamiento.viaje_id == viaje_id,
            self.Alojamiento.fecha_entrada <= hoy,
            self.Alojamiento.fecha_salida > hoy
        ).all()
    
    def obtener_proximos_checkins(self, viaje_id, dias_anticipacion=7):
        """
        Obtener check-ins próximos.
        
        Args:
            viaje_id (int): ID del viaje
            dias_anticipacion (int): Días de anticipación desde hoy
            
        Returns:
            list: Lista de alojamientos con check-in próximo
        """
        fecha_limite = date.today() + timedelta(days=dias_anticipacion)
        
        return self.Alojamiento.query.filter(
            self.Alojamiento.viaje_id == viaje_id,
            self.Alojamiento.fecha_entrada <= fecha_limite,
            self.Alojamiento.fecha_entrada >= date.today()
        ).order_by(self.Alojamiento.fecha_entrada).all()
    
    def obtener_estadisticas_alojamientos(self, viaje_id):
        """
        Calcular estadísticas de alojamientos para un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Estadísticas de alojamientos
        """
        alojamientos = self.obtener_alojamientos_por_viaje(viaje_id)
        total = len(alojamientos)
        
        if total == 0:
            return {
                'total': 0,
                'total_noches': 0,
                'con_desayuno': 0,
                'con_confirmacion': 0,
                'destinos_unicos': 0,
                'gaps_cobertura': 0
            }
        
        # Calcular estadísticas básicas
        noches_info = self.calcular_noches_estancia(viaje_id)
        continuidad_info = self.verificar_continuidad_alojamiento(viaje_id)
        
        # Contar alojamientos con características específicas
        con_desayuno = sum(1 for a in alojamientos if a.incluye_desayuno)
        con_confirmacion = sum(1 for a in alojamientos if a.numero_confirmacion)
        con_pin = sum(1 for a in alojamientos if a.codigo_pin)
        
        # Destinos únicos
        destinos = set(a.destino.lower() for a in alojamientos if a.destino)
        
        return {
            'total': total,
            'total_noches': noches_info['total_noches'],
            'promedio_noches': noches_info['promedio_noches_por_alojamiento'],
            'con_desayuno': con_desayuno,
            'con_confirmacion': con_confirmacion,
            'con_codigo_pin': con_pin,
            'destinos_unicos': len(destinos),
            'gaps_cobertura': continuidad_info['total_gaps'],
            'dias_sin_alojamiento': continuidad_info['dias_sin_alojamiento'],
            'cobertura_completa': continuidad_info['cobertura_completa'],
            'porcentaje_con_desayuno': round((con_desayuno / total * 100), 1),
            'porcentaje_con_confirmacion': round((con_confirmacion / total * 100), 1)
        }
    
    def validar_alojamientos_para_viaje(self, viaje_id):
        """
        Validar la completitud y coherencia de los alojamientos de un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Resultado de validación con recomendaciones
        """
        alojamientos = self.obtener_alojamientos_por_viaje(viaje_id)
        continuidad_info = self.verificar_continuidad_alojamiento(viaje_id)
        
        # Verificar información faltante
        sin_confirmacion = [a for a in alojamientos if not a.numero_confirmacion]
        sin_direccion_completa = [a for a in alojamientos if not a.direccion or len(a.direccion.strip()) < 10]
        
        return {
            'completo': (continuidad_info['cobertura_completa'] and 
                        len(sin_confirmacion) == 0 and 
                        len(sin_direccion_completa) == 0),
            'total_alojamientos': len(alojamientos),
            'sin_confirmacion': len(sin_confirmacion),
            'sin_direccion_completa': len(sin_direccion_completa),
            'gaps_cobertura': continuidad_info['total_gaps'],
            'dias_sin_alojamiento': continuidad_info['dias_sin_alojamiento'],
            'alojamientos_problematicos': sin_confirmacion + sin_direccion_completa,
            'recomendaciones': self._generar_recomendaciones_alojamiento(alojamientos, continuidad_info)
        }
    
    def _generar_recomendaciones_alojamiento(self, alojamientos, continuidad_info):
        """Generar recomendaciones basadas en el análisis de alojamientos."""
        recomendaciones = []
        
        if not alojamientos:
            recomendaciones.append("Agregar información de alojamientos para el viaje")
            return recomendaciones
        
        if not continuidad_info['cobertura_completa']:
            recomendaciones.append(f"Cubrir {continuidad_info['total_gaps']} gaps en alojamiento ({continuidad_info['dias_sin_alojamiento']} días sin alojamiento)")
        
        sin_confirmacion = [a for a in alojamientos if not a.numero_confirmacion]
        if sin_confirmacion:
            recomendaciones.append(f"Agregar números de confirmación para {len(sin_confirmacion)} alojamientos")
        
        sin_direccion = [a for a in alojamientos if not a.direccion or len(a.direccion.strip()) < 10]
        if sin_direccion:
            recomendaciones.append(f"Completar direcciones para {len(sin_direccion)} alojamientos")
        
        # Verificar si hay muchas noches en el mismo destino sin alojamiento continuo
        agrupados = self.agrupar_alojamientos_por_destino(alojamientos[0].viaje_id)
        for destino, alojamientos_destino in agrupados.items():
            if len(alojamientos_destino) > 2:
                recomendaciones.append(f"Considerar consolidar alojamientos en {destino.title()} ({len(alojamientos_destino)} alojamientos)")
        
        return recomendaciones
    
    def eliminar_alojamiento(self, alojamiento_id):
        """
        Eliminar un alojamiento.
        
        Args:
            alojamiento_id (int): ID del alojamiento a eliminar
            
        Returns:
            dict: Resultado con success
        """
        try:
            alojamiento = self.Alojamiento.query.get(alojamiento_id)
            if not alojamiento:
                return {'success': False, 'error': 'Alojamiento no encontrado'}
            
            self.db.session.delete(alojamiento)
            self.db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def actualizar_alojamiento(self, alojamiento_id, **kwargs):
        """
        Actualizar campos de un alojamiento.
        
        Args:
            alojamiento_id (int): ID del alojamiento
            **kwargs: Campos a actualizar
            
        Returns:
            dict: Resultado con success
        """
        try:
            alojamiento = self.Alojamiento.query.get(alojamiento_id)
            if not alojamiento:
                return {'success': False, 'error': 'Alojamiento no encontrado'}
            
            # Actualizar campos permitidos
            campos_permitidos = [
                'nombre', 'destino', 'direccion', 'fecha_entrada', 'fecha_salida',
                'horario_checkin', 'horario_checkout', 'incluye_desayuno',
                'numero_confirmacion', 'codigo_pin', 'numero_checkin', 'notas'
            ]
            
            for campo, valor in kwargs.items():
                if campo in campos_permitidos and hasattr(alojamiento, campo):
                    # Conversiones especiales
                    if campo in ['fecha_entrada', 'fecha_salida'] and isinstance(valor, str):
                        valor = datetime.strptime(valor, '%Y-%m-%d').date() if valor else None
                    elif campo in ['horario_checkin', 'horario_checkout'] and isinstance(valor, str):
                        valor = datetime.strptime(valor, '%H:%M').time() if valor else None
                    elif campo == 'incluye_desayuno':
                        valor = bool(valor)
                    
                    setattr(alojamiento, campo, valor)
            
            self.db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}


# Instancia global del servicio
alojamiento_service = AlojamientoService()
