# -*- coding: utf-8 -*-
"""
Blueprint para rutas de actividades.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

# Crear el blueprint
actividades_bp = Blueprint('actividades', __name__)

# Variables globales para modelos y funciones (se inicializarán después)
Actividad = None
db = None

def init_actividades_routes(models_dict, database_instance):
    """Inicializa las rutas de actividades con los modelos y base de datos necesarios."""
    global Actividad, db
    
    Actividad = models_dict['Actividad']
    db = database_instance

@actividades_bp.route('/viaje/<int:viaje_id>/actividad', methods=['POST'])
def agregar_actividad(viaje_id):
    """Agregar una nueva actividad a un viaje."""
    data = request.get_json()
    
    actividad = Actividad(
        viaje_id=viaje_id,
        destino=data.get('destino', 'general'),
        nombre=data['nombre'],
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        hora=datetime.strptime(data['hora'], '%H:%M').time() if data.get('hora') else None,
        ubicacion=data.get('ubicacion', ''),
        descripcion=data.get('descripcion', '')
    )
    
    db.session.add(actividad)
    db.session.commit()
    
    return jsonify({'success': True, 'actividad_id': actividad.id})

@actividades_bp.route('/actividad/<int:actividad_id>/completar', methods=['POST'])
def completar_actividad(actividad_id):
    """Marcar una actividad como completada o no completada."""
    actividad = Actividad.query.get_or_404(actividad_id)
    actividad.completada = not actividad.completada
    db.session.commit()
    
    return jsonify({'success': True, 'completada': actividad.completada})
