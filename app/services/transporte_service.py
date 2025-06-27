# -*- coding: utf-8 -*-
"""
Servicio para la lógica de negocio de transportes de viaje.
"""

from datetime import datetime, date, timedelta
from collections import defaultdict, OrderedDict


class TransporteService:
    """Servicio para manejar la lógica de negocio relacionada con transportes."""
    
    def __init__(self, database_service=None):
        """Inicializar el servicio de transportes."""
        self.db_service = database_service
        self.db = None
        self.Transporte = None
        self.Viaje = None
        
    def init_models(self, models_dict, database_instance):
        """Inicializar los modelos necesarios."""
        self.Transporte = models_dict['Transporte']
        self.Viaje = models_dict['Viaje']
        self.db = database_instance
        
    def crear_transporte(self, viaje_id, tipo, origen, destino, fecha_salida, fecha_llegada, 
                        hora_salida=None, hora_llegada=None, codigo_reserva='', 
                        aerolinea='', numero_vuelo='', terminal='', puerta='', asiento='', notas=''):
        """
        Crear un nuevo transporte para un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            tipo (str): Tipo de transporte (vuelo, tren, bus, etc.)
            origen (str): Ciudad/aeropuerto de origen
            destino (str): Ciudad/aeropuerto de destino
            fecha_salida (str|date): Fecha de salida
            fecha_llegada (str|date): Fecha de llegada
            hora_salida (str|time): Hora de salida (optional)
            hora_llegada (str|time): Hora de llegada (optional)
            codigo_reserva (str): Código de reserva (optional)
            aerolinea (str): Aerolínea/compañía (optional)
            numero_vuelo (str): Número de vuelo/tren (optional)
            terminal (str): Terminal (optional)
            puerta (str): Puerta de embarque (optional)
            asiento (str): Asiento asignado (optional)
            notas (str): Notas adicionales (optional)
            
        Returns:
            dict: Resultado con success y transporte_id
        """
        try:
            # Convertir fechas si son strings
            if isinstance(fecha_salida, str):
                fecha_salida = datetime.strptime(fecha_salida, '%Y-%m-%d').date()
            if isinstance(fecha_llegada, str):
                fecha_llegada = datetime.strptime(fecha_llegada, '%Y-%m-%d').date()
            
            # Convertir horas si son strings
            if hora_salida and isinstance(hora_salida, str):
                hora_salida = datetime.strptime(hora_salida, '%H:%M').time()
            if hora_llegada and isinstance(hora_llegada, str):
                hora_llegada = datetime.strptime(hora_llegada, '%H:%M').time()
            
            # Crear el transporte
            transporte = self.Transporte(
                viaje_id=viaje_id,
                tipo=tipo,
                origen=origen,
                destino=destino,
                codigo_reserva=codigo_reserva,
                fecha_salida=fecha_salida,
                hora_salida=hora_salida,
                fecha_llegada=fecha_llegada,
                hora_llegada=hora_llegada,
                aerolinea=aerolinea,
                numero_vuelo=numero_vuelo,
                terminal=terminal,
                puerta=puerta,
                asiento=asiento,
                notas=notas
            )
            
            self.db.session.add(transporte)
            self.db.session.commit()
            
            return {'success': True, 'transporte_id': transporte.id}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def obtener_transportes_por_viaje(self, viaje_id):
        """
        Obtener todos los transportes de un viaje ordenados por fecha y hora de salida.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            list: Lista de transportes del viaje
        """
        return self.Transporte.query.filter_by(viaje_id=viaje_id).order_by(
            self.Transporte.fecha_salida, self.Transporte.hora_salida
        ).all()
    
    def agrupar_transportes_por_tipo(self, viaje_id):
        """
        Agrupar transportes de un viaje por tipo.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Diccionario con tipos como claves y listas de transportes como valores
        """
        transportes = self.obtener_transportes_por_viaje(viaje_id)
        transportes_agrupados = defaultdict(list)
        
        for transporte in transportes:
            transportes_agrupados[transporte.tipo].append(transporte)
        
        # Convertir a dict normal y ordenar tipos por prioridad
        tipos_ordenados = ['vuelo', 'tren', 'bus', 'ferry', 'taxi', 'transfer', 'otros']
        resultado = OrderedDict()
        
        # Primero agregar tipos conocidos en orden de prioridad
        for tipo in tipos_ordenados:
            if tipo in transportes_agrupados:
                resultado[tipo] = transportes_agrupados[tipo]
        
        # Agregar tipos no conocidos alfabéticamente
        for tipo in sorted(transportes_agrupados.keys()):
            if tipo not in tipos_ordenados:
                resultado[tipo] = transportes_agrupados[tipo]
        
        return resultado
    
    def obtener_itinerario_transportes(self, viaje_id):
        """
        Obtener el itinerario completo de transportes del viaje con conexiones.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            list: Lista de transportes con información de conexiones
        """
        transportes = self.obtener_transportes_por_viaje(viaje_id)
        itinerario = []
        
        for i, transporte in enumerate(transportes):
            # Calcular tiempo de viaje si hay horas
            tiempo_viaje = None
            if transporte.hora_salida and transporte.hora_llegada:
                # Combinar fecha y hora para cálculo
                salida = datetime.combine(transporte.fecha_salida, transporte.hora_salida)
                llegada = datetime.combine(transporte.fecha_llegada, transporte.hora_llegada)
                
                # Ajustar si la llegada es al día siguiente
                if llegada < salida:
                    llegada += timedelta(days=1)
                
                tiempo_viaje = llegada - salida
            
            # Calcular tiempo de conexión con el siguiente transporte
            tiempo_conexion = None
            siguiente_transporte = None
            if i < len(transportes) - 1:
                siguiente = transportes[i + 1]
                siguiente_transporte = siguiente
                
                if (transporte.hora_llegada and siguiente.hora_salida and 
                    transporte.fecha_llegada and siguiente.fecha_salida):
                    
                    llegada_actual = datetime.combine(transporte.fecha_llegada, transporte.hora_llegada)
                    salida_siguiente = datetime.combine(siguiente.fecha_salida, siguiente.hora_salida)
                    
                    # Ajustar fechas si es necesario
                    if salida_siguiente < llegada_actual:
                        salida_siguiente += timedelta(days=1)
                    
                    tiempo_conexion = salida_siguiente - llegada_actual
            
            itinerario.append({
                'transporte': transporte,
                'tiempo_viaje': tiempo_viaje,
                'tiempo_conexion': tiempo_conexion,
                'siguiente_transporte': siguiente_transporte,
                'es_ultimo': i == len(transportes) - 1
            })
        
        return itinerario
    
    def verificar_conexiones_criticas(self, viaje_id, tiempo_minimo_conexion=timedelta(hours=1)):
        """
        Verificar si hay conexiones muy ajustadas entre transportes.
        
        Args:
            viaje_id (int): ID del viaje
            tiempo_minimo_conexion (timedelta): Tiempo mínimo recomendado entre conexiones
            
        Returns:
            list: Lista de conexiones problemáticas
        """
        itinerario = self.obtener_itinerario_transportes(viaje_id)
        conexiones_criticas = []
        
        for item in itinerario:
            if item['tiempo_conexion'] and item['tiempo_conexion'] < tiempo_minimo_conexion:
                conexiones_criticas.append({
                    'transporte_actual': item['transporte'],
                    'siguiente_transporte': item['siguiente_transporte'],
                    'tiempo_conexion': item['tiempo_conexion'],
                    'tiempo_minimo_recomendado': tiempo_minimo_conexion,
                    'diferencia': tiempo_minimo_conexion - item['tiempo_conexion']
                })
        
        return conexiones_criticas
    
    def obtener_transportes_proximos(self, viaje_id, dias_anticipacion=7):
        """
        Obtener transportes próximos a partir de una fecha.
        
        Args:
            viaje_id (int): ID del viaje
            dias_anticipacion (int): Días de anticipación desde hoy
            
        Returns:
            list: Lista de transportes próximos
        """
        fecha_limite = date.today() + timedelta(days=dias_anticipacion)
        
        return self.Transporte.query.filter(
            self.Transporte.viaje_id == viaje_id,
            self.Transporte.fecha_salida <= fecha_limite,
            self.Transporte.fecha_salida >= date.today()
        ).order_by(self.Transporte.fecha_salida, self.Transporte.hora_salida).all()
    
    def obtener_estadisticas_transportes(self, viaje_id):
        """
        Calcular estadísticas de transportes para un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Estadísticas de transportes
        """
        transportes = self.obtener_transportes_por_viaje(viaje_id)
        total = len(transportes)
        
        # Agrupar por tipo
        tipos = defaultdict(int)
        for transporte in transportes:
            tipos[transporte.tipo] += 1
        
        # Contar los que tienen información completa
        con_hora = sum(1 for t in transportes if t.hora_salida and t.hora_llegada)
        con_codigo_reserva = sum(1 for t in transportes if t.codigo_reserva)
        con_asiento = sum(1 for t in transportes if t.asiento)
        
        # Verificar conexiones críticas
        conexiones_criticas = self.verificar_conexiones_criticas(viaje_id)
        
        return {
            'total': total,
            'por_tipo': dict(tipos),
            'con_horarios_completos': con_hora,
            'con_codigo_reserva': con_codigo_reserva,
            'con_asiento_asignado': con_asiento,
            'conexiones_criticas': len(conexiones_criticas),
            'porcentaje_info_completa': round((con_hora / total * 100) if total > 0 else 0, 1)
        }
    
    def validar_transportes_para_viaje(self, viaje_id):
        """
        Validar la completitud y coherencia de los transportes de un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Resultado de validación con recomendaciones
        """
        transportes = self.obtener_transportes_por_viaje(viaje_id)
        conexiones_criticas = self.verificar_conexiones_criticas(viaje_id)
        
        # Verificar información faltante
        sin_codigo_reserva = [t for t in transportes if not t.codigo_reserva]
        sin_horarios = [t for t in transportes if not t.hora_salida or not t.hora_llegada]
        sin_detalles = [t for t in transportes if not t.aerolinea and not t.numero_vuelo]
        
        return {
            'completo': len(sin_codigo_reserva) == 0 and len(sin_horarios) == 0 and len(conexiones_criticas) == 0,
            'total_transportes': len(transportes),
            'sin_codigo_reserva': len(sin_codigo_reserva),
            'sin_horarios_completos': len(sin_horarios),
            'sin_detalles_compania': len(sin_detalles),
            'conexiones_criticas': len(conexiones_criticas),
            'transportes_problematicos': sin_codigo_reserva + sin_horarios,
            'recomendaciones': self._generar_recomendaciones_transporte(transportes, conexiones_criticas)
        }
    
    def _generar_recomendaciones_transporte(self, transportes, conexiones_criticas):
        """Generar recomendaciones basadas en el análisis de transportes."""
        recomendaciones = []
        
        if not transportes:
            recomendaciones.append("Agregar información de transportes para el viaje")
        
        sin_reserva = [t for t in transportes if not t.codigo_reserva]
        if sin_reserva:
            recomendaciones.append(f"Agregar códigos de reserva para {len(sin_reserva)} transportes")
        
        sin_horarios = [t for t in transportes if not t.hora_salida or not t.hora_llegada]
        if sin_horarios:
            recomendaciones.append(f"Completar horarios para {len(sin_horarios)} transportes")
        
        if conexiones_criticas:
            recomendaciones.append(f"Revisar {len(conexiones_criticas)} conexiones muy ajustadas")
        
        return recomendaciones
    
    def eliminar_transporte(self, transporte_id):
        """
        Eliminar un transporte.
        
        Args:
            transporte_id (int): ID del transporte a eliminar
            
        Returns:
            dict: Resultado con success
        """
        try:
            transporte = self.Transporte.query.get(transporte_id)
            if not transporte:
                return {'success': False, 'error': 'Transporte no encontrado'}
            
            self.db.session.delete(transporte)
            self.db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def actualizar_transporte(self, transporte_id, **kwargs):
        """
        Actualizar campos de un transporte.
        
        Args:
            transporte_id (int): ID del transporte
            **kwargs: Campos a actualizar
            
        Returns:
            dict: Resultado con success
        """
        try:
            transporte = self.Transporte.query.get(transporte_id)
            if not transporte:
                return {'success': False, 'error': 'Transporte no encontrado'}
            
            # Actualizar campos permitidos
            campos_permitidos = [
                'tipo', 'origen', 'destino', 'codigo_reserva', 'fecha_salida', 'hora_salida',
                'fecha_llegada', 'hora_llegada', 'aerolinea', 'numero_vuelo', 'terminal',
                'puerta', 'asiento', 'notas'
            ]
            
            for campo, valor in kwargs.items():
                if campo in campos_permitidos and hasattr(transporte, campo):
                    # Conversiones especiales
                    if campo in ['fecha_salida', 'fecha_llegada'] and isinstance(valor, str):
                        valor = datetime.strptime(valor, '%Y-%m-%d').date() if valor else None
                    elif campo in ['hora_salida', 'hora_llegada'] and isinstance(valor, str):
                        valor = datetime.strptime(valor, '%H:%M').time() if valor else None
                    
                    setattr(transporte, campo, valor)
            
            self.db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}


# Instancia global del servicio
transporte_service = TransporteService()
