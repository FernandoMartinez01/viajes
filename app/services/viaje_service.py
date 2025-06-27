# -*- coding: utf-8 -*-
"""
Servicio para lógica de negocio de viajes.
"""

from datetime import datetime, date
from collections import OrderedDict


class ViajeService:
    """Servicio centralizado para operaciones de viajes."""
    
    def __init__(self):
        self._models = None
        self._db = None
    
    def init_service(self, models, db):
        """Inicializa el servicio con los modelos y base de datos."""
        self._models = models
        self._db = db
        print("🧳 ViajeService inicializado")
    
    def agrupar_actividades_por_destino(self, viaje):
        """
        Agrupa y ordena las actividades de un viaje por destino y fecha/hora.
        
        Args:
            viaje: Instancia del modelo Viaje
            
        Returns:
            OrderedDict: Actividades agrupadas por destino y ordenadas
        """
        actividades_agrupadas = {}
        
        # Agrupar actividades por destino
        for actividad in viaje.actividades:
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
    
    def eliminar_viaje_completo(self, viaje_id):
        """
        Elimina un viaje y todos sus elementos relacionados.
        
        Args:
            viaje_id: ID del viaje a eliminar
            
        Returns:
            dict: Resultado de la operación con éxito y mensaje
        """
        try:
            Viaje = self._models['Viaje']
            Parada = self._models['Parada']
            Gasto = self._models['Gasto']
            Actividad = self._models['Actividad']
            Documento = self._models['Documento']
            Transporte = self._models['Transporte']
            Alojamiento = self._models['Alojamiento']
            
            viaje = Viaje.query.get_or_404(viaje_id)
            nombre_viaje = viaje.nombre
            
            print(f"Iniciando eliminación del viaje: {nombre_viaje} (ID: {viaje_id})")
            
            # Contar elementos relacionados antes de eliminar (para logs)
            num_paradas = len(viaje.paradas)
            num_gastos = len(viaje.gastos)
            num_actividades = len(viaje.actividades)
            num_documentos = len(viaje.documentos)
            num_transportes = len(viaje.transportes)
            num_alojamientos = len(viaje.alojamientos)
            
            print(f"Elementos a eliminar:")
            print(f"  - Paradas: {num_paradas}")
            print(f"  - Gastos: {num_gastos}")
            print(f"  - Actividades: {num_actividades}")
            print(f"  - Documentos: {num_documentos}")
            print(f"  - Transportes: {num_transportes}")
            print(f"  - Alojamientos: {num_alojamientos}")
            
            # Eliminar explícitamente elementos relacionados
            # (aunque el cascade debería manejar esto automáticamente)
            
            # Eliminar paradas
            Parada.query.filter_by(viaje_id=viaje_id).delete()
            print("  ✓ Paradas eliminadas")
            
            # Eliminar gastos
            Gasto.query.filter_by(viaje_id=viaje_id).delete()
            print("  ✓ Gastos eliminados")
            
            # Eliminar actividades
            Actividad.query.filter_by(viaje_id=viaje_id).delete()
            print("  ✓ Actividades eliminadas")
            
            # Eliminar documentos
            Documento.query.filter_by(viaje_id=viaje_id).delete()
            print("  ✓ Documentos eliminados")
            
            # Eliminar transportes
            Transporte.query.filter_by(viaje_id=viaje_id).delete()
            print("  ✓ Transportes eliminados")
            
            # Eliminar alojamientos
            Alojamiento.query.filter_by(viaje_id=viaje_id).delete()
            print("  ✓ Alojamientos eliminados")
            
            # Finalmente, eliminar el viaje
            self._db.session.delete(viaje)
            print("  ✓ Viaje eliminado")
            
            # Commit de todos los cambios
            self._db.session.commit()
            print(f"✅ Eliminación completada exitosamente")
            
            total_elementos = num_paradas + num_gastos + num_actividades + num_documentos + num_transportes + num_alojamientos
            
            return {
                'success': True,
                'message': f'Viaje "{nombre_viaje}" y {total_elementos} elementos relacionados eliminados correctamente'
            }
            
        except Exception as e:
            print(f"❌ Error al eliminar viaje: {str(e)}")
            self._db.session.rollback()
            return {
                'success': False,
                'message': f'Error al eliminar el viaje: {str(e)}'
            }
    
    def reordenar_paradas_por_fecha(self, viaje_id):
        """
        Reordena automáticamente todas las paradas de un viaje por fecha de llegada.
        En caso de fechas iguales, usa estos criterios de desempate:
        1. Fecha de salida (más temprana primero)
        2. Nombre del destino (alfabéticamente)
        3. ID de la parada (orden de creación)
        
        Args:
            viaje_id: ID del viaje cuyas paradas se van a reordenar
        """
        try:
            Parada = self._models['Parada']
            
            print(f"Reordenando paradas del viaje {viaje_id} por fecha de llegada...")
            
            # Obtener todas las paradas del viaje
            paradas = Parada.query.filter_by(viaje_id=viaje_id).all()
            
            if len(paradas) <= 1:
                print("Solo hay una parada o menos, no se necesita reordenar")
                return
            
            # Ordenar por múltiples criterios
            paradas_ordenadas = sorted(paradas, key=lambda p: (
                p.fecha_llegada,           # 1. Fecha de llegada (principal)
                p.fecha_salida,            # 2. Fecha de salida (desempate)
                p.destino.lower(),         # 3. Destino alfabéticamente
                p.id                       # 4. ID (orden de creación)
            ))
            
            print("Nueva secuencia de paradas:")
            
            # PASO 1: Asignar órdenes temporales únicos (negativos para evitar conflictos)
            print("Paso 1: Asignando órdenes temporales...")
            for i, parada in enumerate(paradas_ordenadas):
                orden_temporal = -(i + 1000)  # Usar números negativos muy grandes
                print(f"  Temp {orden_temporal}: {parada.destino} - Llegada: {parada.fecha_llegada}")
                parada.orden = orden_temporal
            
            # Hacer flush para aplicar cambios temporales
            self._db.session.flush()
            
            # PASO 2: Asignar los órdenes finales correctos
            print("Paso 2: Asignando órdenes finales...")
            for i, parada in enumerate(paradas_ordenadas):
                nuevo_orden = i + 1
                print(f"  {nuevo_orden}. {parada.destino} - Llegada: {parada.fecha_llegada}")
                parada.orden = nuevo_orden
            
            # Commit final
            self._db.session.commit()
            print("Reordenamiento automático completado exitosamente")
            
        except Exception as e:
            print(f"Error al reordenar paradas por fecha: {str(e)}")
            self._db.session.rollback()
            raise

    def reordenar_parada_especifica(self, parada_id, nuevo_orden):
        """
        Reordena una parada específica a una nueva posición.
        
        Args:
            parada_id: ID de la parada a reordenar
            nuevo_orden: Nueva posición (1-indexed)
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            Parada = self._models['Parada']
            
            parada = Parada.query.get_or_404(parada_id)
            viaje_id = parada.viaje_id
            orden_actual = parada.orden
            
            print(f"Reordenando parada {parada_id} del orden {orden_actual} al orden {nuevo_orden}")
            
            if orden_actual == nuevo_orden:
                print("El orden no ha cambiado, no se necesita actualizar")
                return {'success': True}
            
            # Obtener todas las paradas del viaje ordenadas
            paradas = Parada.query.filter_by(viaje_id=viaje_id).order_by(Parada.orden).all()
            
            # Crear una lista temporal con los nuevos órdenes
            paradas_temp = []
            for p in paradas:
                if p.id == parada_id:
                    # Esta es la parada que estamos moviendo
                    continue
                paradas_temp.append(p)
            
            # Insertar la parada movida en la nueva posición
            # Ajustar posición ya que nuevo_orden es 1-indexed
            nueva_posicion = nuevo_orden - 1
            if nueva_posicion < 0:
                nueva_posicion = 0
            elif nueva_posicion > len(paradas_temp):
                nueva_posicion = len(paradas_temp)
                
            paradas_temp.insert(nueva_posicion, parada)
            
            # Usar valores temporales negativos para evitar conflictos de constraint
            print("Asignando órdenes temporales...")
            for i, p in enumerate(paradas_temp):
                p.orden = -(i + 1)  # Valores negativos temporales
            
            self._db.session.flush()  # Aplicar cambios temporales
            
            # Ahora asignar los órdenes finales correctos
            print("Asignando órdenes finales...")
            for i, p in enumerate(paradas_temp):
                p.orden = i + 1  # Órdenes finales correctos
            
            self._db.session.commit()
            
            print(f"Reordenamiento completado exitosamente. Nueva secuencia:")
            for p in paradas_temp:
                print(f"  Parada {p.id} ({p.destino}): orden {p.orden}")
            
            return {'success': True}
            
        except Exception as e:
            print(f"Error al reordenar parada: {str(e)}")
            self._db.session.rollback()
            return {'success': False, 'error': str(e)}


# Instancia global del servicio
viaje_service = ViajeService()
