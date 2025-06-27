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
    
    # Importar y configurar el servicio de viajes
    from app.services import viaje_service
    viaje_service.init_service(models_dict, database_instance)

@viajes_bp.route('/viaje/<int:viaje_id>')
def ver_viaje(viaje_id):
    """Mostrar los detalles de un viaje específico."""
    viaje = Viaje.query.get_or_404(viaje_id)
    
    # Usar el servicio para agrupar actividades
    from app.services import viaje_service
    actividades_ordenadas = viaje_service.agrupar_actividades_por_destino(viaje)
    
    return render_template('viaje.html', 
                         viaje=viaje, 
                         actividades_agrupadas=actividades_ordenadas,
                         hoy=date.today())

@viajes_bp.route('/viaje/<int:viaje_id>/eliminar', methods=['POST'])
def eliminar_viaje(viaje_id):
    """Eliminar un viaje y todos sus elementos relacionados."""
    # Usar el servicio para eliminar el viaje
    from app.services import viaje_service
    resultado = viaje_service.eliminar_viaje_completo(viaje_id)
    
    if resultado['success']:
        return jsonify(resultado)
    else:
        return jsonify(resultado), 500

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
    from app.services import viaje_service
    viaje_service.reordenar_paradas_por_fecha(viaje_id)
    
    return jsonify({'success': True, 'parada_id': parada.id})

@viajes_bp.route('/viaje/<int:viaje_id>/reordenar-por-fecha', methods=['POST'])
def reordenar_viaje_por_fecha(viaje_id):
    """Endpoint para reordenar manualmente un viaje por fechas."""
    try:
        from app.services import viaje_service
        viaje_service.reordenar_paradas_por_fecha(viaje_id)
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
        
        # Usar el servicio para reordenar la parada
        from app.services import viaje_service
        resultado = viaje_service.reordenar_parada_especifica(parada_id, nuevo_orden)
        
        if resultado['success']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 500
        
    except Exception as e:
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
        from app.services import viaje_service
        viaje_service.reordenar_paradas_por_fecha(viaje_id)
        
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
                from app.services import viaje_service
                viaje_service.reordenar_paradas_por_fecha(viaje.id)
                reordenados += 1
        
        return jsonify({
            'success': True, 
            'message': f'Se reordenaron {reordenados} viajes correctamente'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
