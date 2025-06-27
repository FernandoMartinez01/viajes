# -*- coding: utf-8 -*-
"""
Servicio para la lógica de negocio de gastos.
"""

from datetime import datetime


class GastoService:
    """Servicio para manejar la lógica de negocio relacionada con gastos."""
    
    def __init__(self, database_service):
        """Inicializar el servicio de gastos."""
        self.db_service = database_service
        self.db = None
        self.Gasto = None
        self.Viaje = None
        
    def init_models(self, models_dict, database_instance):
        """Inicializar los modelos necesarios."""
        self.Gasto = models_dict['Gasto']
        self.Viaje = models_dict['Viaje']
        self.db = database_instance
        
    def crear_gasto(self, viaje_id, categoria, descripcion, monto, fecha, moneda='USD'):
        """
        Crear un nuevo gasto y actualizar el presupuesto del viaje.
        
        Args:
            viaje_id (int): ID del viaje
            categoria (str): Categoría del gasto
            descripcion (str): Descripción del gasto
            monto (float): Monto del gasto
            fecha (str|date): Fecha del gasto
            moneda (str): Moneda del gasto (default: USD)
            
        Returns:
            dict: Resultado con success y gasto_id
        """
        try:
            # Convertir fecha si es string
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            
            # Crear el gasto
            gasto = self.Gasto(
                viaje_id=viaje_id,
                categoria=categoria,
                descripcion=descripcion,
                monto=float(monto),
                fecha=fecha,
                moneda=moneda
            )
            
            self.db.session.add(gasto)
            self.db.session.flush()  # Para que el gasto esté disponible en la relación
            
            # Actualizar presupuesto gastado del viaje
            self._actualizar_presupuesto_viaje(viaje_id)
            
            self.db.session.commit()
            
            return {'success': True, 'gasto_id': gasto.id}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def _actualizar_presupuesto_viaje(self, viaje_id):
        """
        Actualizar el presupuesto gastado de un viaje sumando todos sus gastos.
        
        Args:
            viaje_id (int): ID del viaje
        """
        viaje = self.Viaje.query.get(viaje_id)
        if viaje:
            viaje.presupuesto_gastado = sum(g.monto for g in viaje.gastos)
    
    def obtener_gastos_por_viaje(self, viaje_id):
        """
        Obtener todos los gastos de un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            list: Lista de gastos del viaje
        """
        return self.Gasto.query.filter_by(viaje_id=viaje_id).order_by(self.Gasto.fecha.desc()).all()
    
    def obtener_gastos_por_categoria(self, viaje_id):
        """
        Agrupar gastos de un viaje por categoría.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            dict: Diccionario con categorías como claves y totales como valores
        """
        gastos = self.obtener_gastos_por_viaje(viaje_id)
        categorias = {}
        
        for gasto in gastos:
            categoria = gasto.categoria
            if categoria not in categorias:
                categorias[categoria] = 0
            categorias[categoria] += gasto.monto
            
        return categorias
    
    def calcular_total_gastado(self, viaje_id):
        """
        Calcular el total gastado en un viaje.
        
        Args:
            viaje_id (int): ID del viaje
            
        Returns:
            float: Total gastado
        """
        gastos = self.obtener_gastos_por_viaje(viaje_id)
        return sum(g.monto for g in gastos)
    
    def eliminar_gasto(self, gasto_id):
        """
        Eliminar un gasto y actualizar el presupuesto del viaje.
        
        Args:
            gasto_id (int): ID del gasto a eliminar
            
        Returns:
            dict: Resultado con success
        """
        try:
            gasto = self.Gasto.query.get(gasto_id)
            if not gasto:
                return {'success': False, 'error': 'Gasto no encontrado'}
            
            viaje_id = gasto.viaje_id
            
            self.db.session.delete(gasto)
            
            # Actualizar presupuesto gastado del viaje
            self._actualizar_presupuesto_viaje(viaje_id)
            
            self.db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.db.session.rollback()
            return {'success': False, 'error': str(e)}


# Instancia global del servicio
gasto_service = GastoService(None)  # Se inicializará el database_service después
