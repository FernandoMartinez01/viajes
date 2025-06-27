# -*- coding: utf-8 -*-
"""
Blueprint para rutas de viajes y paradas.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime, date
from collections import OrderedDict

# Crear el blueprint
viajes_bp = Blueprint('viajes', __name__)

# Variables globales para modelos y funciones (se inicializarán después)
Viaje = None
Parada = None
db = None

def init_viajes_routes(models_dict, database_instance):
    """Inicializa las rutas de viajes con los modelos y base de datos necesarios."""
    global Viaje, Parada, db
    
    Viaje = models_dict['Viaje']
    Parada = models_dict['Parada']
    db = database_instance

@viajes_bp.route('/viaje/<int:viaje_id>')
def ver_viaje(viaje_id):
    """Mostrar los detalles de un viaje específico."""
    viaje = Viaje.query.get_or_404(viaje_id)
    
    # Agrupar y ordenar actividades por destino y fecha/hora
    actividades_agrupadas = {}
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
    
    return render_template('viaje.html', 
                         viaje=viaje, 
                         actividades_agrupadas=actividades_ordenadas,
                         hoy=date.today())

@viajes_bp.route('/viaje/<int:viaje_id>/eliminar', methods=['POST'])
def eliminar_viaje(viaje_id):
    """Eliminar un viaje y todos sus elementos relacionados."""
    try:
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
        
        # Importar modelos dinámicamente para evitar problemas de inicialización
        from app.models import Gasto, Actividad, Documento, Transporte, Alojamiento
        
        # Verificación adicional: eliminar explícitamente elementos relacionados
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
        db.session.delete(viaje)
        print("  ✓ Viaje eliminado")
        
        # Commit de todos los cambios
        db.session.commit()
        print(f"✅ Eliminación completada exitosamente")
        
        total_elementos = num_paradas + num_gastos + num_actividades + num_documentos + num_transportes + num_alojamientos
        
        return jsonify({
            'success': True,
            'message': f'Viaje "{nombre_viaje}" y {total_elementos} elementos relacionados eliminados correctamente'
        })
        
    except Exception as e:
        print(f"❌ Error al eliminar viaje: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al eliminar el viaje: {str(e)}'
        }), 500

@viajes_bp.route('/nuevo-viaje', methods=['GET', 'POST'])
def nuevo_viaje():
    """Crear un nuevo viaje."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Crear el viaje principal
        viaje = Viaje(
            nombre=data['nombre'],
            fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date(),
            fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date(),
            presupuesto_total=float(data.get('presupuesto_total', 0)),
            notas=data.get('notas', '')
        )
        
        db.session.add(viaje)
        db.session.flush()  # Para obtener el ID del viaje
        
        # Procesar paradas
        paradas_data = data.get('paradas', [])
        if isinstance(paradas_data, str):
            import json
            paradas_data = json.loads(paradas_data)
        
        for i, parada_data in enumerate(paradas_data):
            parada = Parada(
                viaje_id=viaje.id,
                destino=parada_data['destino'],
                orden=i + 1,
                fecha_llegada=datetime.strptime(parada_data['fecha_llegada'], '%Y-%m-%d').date(),
                fecha_salida=datetime.strptime(parada_data['fecha_salida'], '%Y-%m-%d').date(),
                notas=parada_data.get('notas', '')
            )
            db.session.add(parada)
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'viaje_id': viaje.id})
        return redirect(url_for('viajes.ver_viaje', viaje_id=viaje.id))
    
    return render_template('nuevo_viaje.html')

@viajes_bp.route('/viaje/<int:viaje_id>/parada', methods=['POST'])
def agregar_parada(viaje_id):
    """Agregar una nueva parada a un viaje."""
    data = request.get_json()
    
    parada = Parada(
        viaje_id=viaje_id,
        destino=data['destino'],
        orden=999,  # Orden temporal, se reorganizará automáticamente
        fecha_llegada=datetime.strptime(data['fecha_llegada'], '%Y-%m-%d').date(),
        fecha_salida=datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date(),
        notas=data.get('notas', '')
    )
    
    db.session.add(parada)
    db.session.commit()
    
    # Reordenar automáticamente todas las paradas por fecha
    reordenar_paradas_por_fecha(viaje_id)
    
    return jsonify({'success': True, 'parada_id': parada.id})

def reordenar_paradas_por_fecha(viaje_id):
    """
    Reordena automáticamente todas las paradas de un viaje por fecha de llegada.
    En caso de fechas iguales, usa estos criterios de desempate:
    1. Fecha de salida (más temprana primero)
    2. Nombre del destino (alfabéticamente)
    3. ID de la parada (orden de creación)
    """
    try:
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
        db.session.flush()
        
        # PASO 2: Asignar los órdenes finales correctos
        print("Paso 2: Asignando órdenes finales...")
        for i, parada in enumerate(paradas_ordenadas):
            nuevo_orden = i + 1
            print(f"  {nuevo_orden}. {parada.destino} - Llegada: {parada.fecha_llegada}")
            parada.orden = nuevo_orden
        
        # Commit final
        db.session.commit()
        print("Reordenamiento automático completado exitosamente")
        
    except Exception as e:
        print(f"Error al reordenar paradas por fecha: {str(e)}")
        db.session.rollback()
        raise

@viajes_bp.route('/viaje/<int:viaje_id>/reordenar-por-fecha', methods=['POST'])
def reordenar_viaje_por_fecha(viaje_id):
    """Endpoint para reordenar manualmente un viaje por fechas."""
    try:
        reordenar_paradas_por_fecha(viaje_id)
        return jsonify({'success': True, 'message': 'Paradas reordenadas por fecha exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@viajes_bp.route('/parada/<int:parada_id>/reordenar', methods=['POST'])
def reordenar_parada(parada_id):
    """Reordenar una parada específica a una nueva posición."""
    try:
        data = request.get_json()
        if not data or 'nuevo_orden' not in data:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
            
        nuevo_orden = int(data['nuevo_orden'])
        
        parada = Parada.query.get_or_404(parada_id)
        viaje_id = parada.viaje_id
        orden_actual = parada.orden
        
        print(f"Reordenando parada {parada_id} del orden {orden_actual} al orden {nuevo_orden}")
        
        if orden_actual == nuevo_orden:
            print("El orden no ha cambiado, no se necesita actualizar")
            return jsonify({'success': True})
        
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
        
        db.session.flush()  # Aplicar cambios temporales
        
        # Ahora asignar los órdenes finales correctos
        print("Asignando órdenes finales...")
        for i, p in enumerate(paradas_temp):
            p.orden = i + 1  # Órdenes finales correctos
        
        db.session.commit()
        
        print(f"Reordenamiento completado exitosamente. Nueva secuencia:")
        for p in paradas_temp:
            print(f"  Parada {p.id} ({p.destino}): orden {p.orden}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error al reordenar parada: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@viajes_bp.route('/parada/<int:parada_id>', methods=['PUT'])
def editar_parada(parada_id):
    """Editar los datos de una parada."""
    try:
        data = request.get_json()
        parada = Parada.query.get_or_404(parada_id)
        viaje_id = parada.viaje_id
        
        # Actualizar campos
        parada.destino = data['destino']
        parada.fecha_llegada = datetime.strptime(data['fecha_llegada'], '%Y-%m-%d').date()
        parada.fecha_salida = datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date()
        parada.notas = data.get('notas', '')
        
        db.session.commit()
        
        # Reordenar automáticamente todas las paradas por fecha
        reordenar_paradas_por_fecha(viaje_id)
        
        return jsonify({
            'success': True,
            'message': 'Parada actualizada y reordenada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar parada: {str(e)}'
        }), 500

@viajes_bp.route('/parada/<int:parada_id>', methods=['DELETE'])
def eliminar_parada(parada_id):
    """Eliminar una parada."""
    try:
        parada = Parada.query.get_or_404(parada_id)
        viaje_id = parada.viaje_id
        orden_eliminada = parada.orden
        
        # Eliminar la parada
        db.session.delete(parada)
        
        # Reordenar las paradas restantes
        Parada.query.filter(
            Parada.viaje_id == viaje_id,
            Parada.orden > orden_eliminada
        ).update({Parada.orden: Parada.orden - 1})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Parada eliminada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al eliminar parada: {str(e)}'
        }), 500

@viajes_bp.route('/admin/reordenar-todos-viajes', methods=['POST'])
def reordenar_todos_viajes():
    """Endpoint administrativo para reordenar todas las paradas de todos los viajes por fecha."""
    try:
        viajes = Viaje.query.all()
        reordenados = 0
        
        for viaje in viajes:
            if len(viaje.paradas) > 1:
                print(f"Reordenando viaje: {viaje.nombre} (ID: {viaje.id})")
                reordenar_paradas_por_fecha(viaje.id)
                reordenados += 1
        
        return jsonify({
            'success': True, 
            'message': f'Se reordenaron {reordenados} viajes correctamente'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
