# -*- coding: utf-8 -*-
"""
Servicio para la lógica de negocio de documentos de viaje.
"""

from datetime import datetime, date, timedelta
from collections import defaultdict


class DocumentoService:
    """Servicio para manejar la lógica de negocio relacionada con documentos de viaje."""
    
    def __init__(self, database_service=None):
        """Inicializar el servicio de documentos."""
        self.db_service = database_service
        self.db = None
        self.Documento = None
        self.Viaje = None
        
    def init_models(self, models_dict, database_instance):
        """Inicializar los modelos necesarios."""
        self.Documento = models_dict['Documento']
        self.Viaje = models_dict['Viaje']
        self.db = database_instance
        
    def crear_documento(self, viaje_id, tipo, nombre, numero='', fecha_vencimiento=None, notas=''):
        """
        Crear un nuevo documento para un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            tipo (str): Tipo de documento (pasaporte, visa, seguro, etc.)
            nombre (str): Nombre del documento
            numero (str): Número del documento (optional)
            fecha_vencimiento (str|date): Fecha de vencimiento (optional)
            notas (str): Notas adicionales (optional)
            
        Returns:
            dict: Resultado con success y documento_id
        """
        try:
            # Convertir fecha si es string no vacío
            if fecha_vencimiento and isinstance(fecha_vencimiento, str) and fecha_vencimiento.strip():
                fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
            else:
                fecha_vencimiento = None  # Si está vacío o es None, usar None
            
            # Crear el documento
            documento = self.Documento(
                viaje_id=viaje_id,
                tipo=tipo,
                nombre=nombre,
                numero=numero,
                fecha_vencimiento=fecha_vencimiento,
                notas=notas
            )
            
            self.db.session.add(documento)
            self.db.session.commit()
            
            return {'success': True, 'documento_id': documento.id}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def obtener_documentos_por_viaje(self, viaje_id):
        """
        Obtener todos los documentos de un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            list: Lista de documentos del viaje
        """
        return self.Documento.query.filter_by(viaje_id=viaje_id).order_by(
            self.Documento.tipo, self.Documento.nombre
        ).all()
    
    def agrupar_documentos_por_tipo(self, viaje_id):
        """
        Agrupar documentos de un viaje por tipo.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Diccionario con tipos como claves y listas de documentos como valores
        """
        documentos = self.obtener_documentos_por_viaje(viaje_id)
        documentos_agrupados = defaultdict(list)
        
        for documento in documentos:
            documentos_agrupados[documento.tipo].append(documento)
        
        # Convertir a dict normal y ordenar tipos
        tipos_ordenados = ['pasaporte', 'visa', 'seguro', 'reserva', 'ticket', 'otros']
        resultado = {}
        
        # Primero agregar tipos conocidos en orden
        for tipo in tipos_ordenados:
            if tipo in documentos_agrupados:
                resultado[tipo] = documentos_agrupados[tipo]
        
        # Agregar tipos no conocidos alfabéticamente
        for tipo in sorted(documentos_agrupados.keys()):
            if tipo not in tipos_ordenados:
                resultado[tipo] = documentos_agrupados[tipo]
        
        return resultado
    
    def verificar_vencimientos(self, viaje_id, dias_anticipacion=30):
        """
        Verificar documentos que están próximos a vencer o ya vencidos.
        
        Args:
            viaje_id (int): ID del viaje
            dias_anticipacion (int): Días de anticipación para alertas
            
        Returns:
            dict: Diccionario con documentos categorizados por estado de vencimiento
        """
        documentos = self.obtener_documentos_por_viaje(viaje_id)
        hoy = date.today()
        fecha_alerta = hoy + timedelta(days=dias_anticipacion)
        
        resultado = {
            'vencidos': [],
            'por_vencer': [],
            'vigentes': [],
            'sin_fecha': []
        }
        
        for documento in documentos:
            if not documento.fecha_vencimiento:
                resultado['sin_fecha'].append(documento)
            elif documento.fecha_vencimiento < hoy:
                resultado['vencidos'].append(documento)
            elif documento.fecha_vencimiento <= fecha_alerta:
                resultado['por_vencer'].append(documento)
            else:
                resultado['vigentes'].append(documento)
        
        return resultado
    
    def obtener_documentos_criticos(self, viaje_id):
        """
        Obtener documentos críticos para el viaje (vencidos o por vencer pronto).
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            list: Lista de documentos que requieren atención
        """
        vencimientos = self.verificar_vencimientos(viaje_id, dias_anticipacion=15)
        return vencimientos['vencidos'] + vencimientos['por_vencer']
    
    def obtener_estadisticas_documentos(self, viaje_id):
        """
        Calcular estadísticas de documentos para un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Estadísticas de documentos
        """
        documentos = self.obtener_documentos_por_viaje(viaje_id)
        vencimientos = self.verificar_vencimientos(viaje_id)
        
        total = len(documentos)
        con_fecha = sum(1 for d in documentos if d.fecha_vencimiento)
        sin_fecha = total - con_fecha
        
        # Agrupar por tipo
        tipos = defaultdict(int)
        for documento in documentos:
            tipos[documento.tipo] += 1
        
        return {
            'total': total,
            'con_fecha_vencimiento': con_fecha,
            'sin_fecha_vencimiento': sin_fecha,
            'vencidos': len(vencimientos['vencidos']),
            'por_vencer': len(vencimientos['por_vencer']),
            'vigentes': len(vencimientos['vigentes']),
            'por_tipo': dict(tipos),
            'requieren_atencion': len(vencimientos['vencidos']) + len(vencimientos['por_vencer'])
        }
    
    def validar_documentos_para_viaje(self, viaje_id):
        """
        Validar que se tienen los documentos esenciales para un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Resultado de validación con recomendaciones
        """
        documentos = self.obtener_documentos_por_viaje(viaje_id)
        tipos_presentes = set(d.tipo.lower() for d in documentos)
        
        # Documentos esenciales recomendados
        esenciales = ['pasaporte', 'visa', 'seguro']
        recomendados = ['reserva', 'ticket']
        
        faltantes_esenciales = [tipo for tipo in esenciales if tipo not in tipos_presentes]
        faltantes_recomendados = [tipo for tipo in recomendados if tipo not in tipos_presentes]
        
        # Verificar vencimientos críticos
        criticos = self.obtener_documentos_criticos(viaje_id)
        
        return {
            'completo': len(faltantes_esenciales) == 0 and len(criticos) == 0,
            'faltantes_esenciales': faltantes_esenciales,
            'faltantes_recomendados': faltantes_recomendados,
            'documentos_criticos': criticos,
            'total_documentos': len(documentos)
        }
    
    def eliminar_documento(self, documento_id):
        """
        Eliminar un documento.
        
        Args:
            documento_id (int): ID del documento a eliminar
            
        Returns:
            dict: Resultado con success
        """
        try:
            documento = self.Documento.query.get(documento_id)
            if not documento:
                return {'success': False, 'error': 'Documento no encontrado'}
            
            self.db.session.delete(documento)
            self.db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def actualizar_documento(self, documento_id, **kwargs):
        """
        Actualizar campos de un documento.
        
        Args:
            documento_id (int): ID del documento
            **kwargs: Campos a actualizar
            
        Returns:
            dict: Resultado con success
        """
        try:
            documento = self.Documento.query.get(documento_id)
            if not documento:
                return {'success': False, 'error': 'Documento no encontrado'}
            
            # Actualizar campos permitidos
            campos_permitidos = ['tipo', 'nombre', 'numero', 'fecha_vencimiento', 'notas']
            
            for campo, valor in kwargs.items():
                if campo in campos_permitidos and hasattr(documento, campo):
                    # Conversiones especiales
                    if campo == 'fecha_vencimiento' and isinstance(valor, str):
                        valor = datetime.strptime(valor, '%Y-%m-%d').date() if valor else None
                    
                    setattr(documento, campo, valor)
            
            self.db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}


# Instancia global del servicio
documento_service = DocumentoService()
