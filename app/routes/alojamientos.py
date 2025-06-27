# -*- coding: utf-8 -*-
"""
Blueprint para rutas de alojamientos.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

# Crear el blueprint
alojamientos_bp = Blueprint('alojamientos', __name__)

# Variables globales para modelos y funciones (se inicializarán después)
Alojamiento = None
db = None

def init_alojamientos_routes(models_dict, database_instance):
    """Inicializa las rutas de alojamientos con los modelos y base de datos necesarios."""
    global Alojamiento, db
    
    Alojamiento = models_dict['Alojamiento']
    db = database_instance

@alojamientos_bp.route('/viaje/<int:viaje_id>/alojamiento', methods=['POST'])
def agregar_alojamiento(viaje_id):
    """Agregar un nuevo alojamiento a un viaje."""
    data = request.get_json()
    
    alojamiento = Alojamiento(
        viaje_id=viaje_id,
        destino=data['destino'],
        nombre=data['nombre'],
        direccion=data['direccion'],
        fecha_entrada=datetime.strptime(data['fecha_entrada'], '%Y-%m-%d').date(),
        horario_checkin=datetime.strptime(data['horario_checkin'], '%H:%M').time(),
        fecha_salida=datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date(),
        horario_checkout=datetime.strptime(data['horario_checkout'], '%H:%M').time(),
        incluye_desayuno=data.get('incluye_desayuno', False),
        numero_confirmacion=data.get('numero_confirmacion', ''),
        codigo_pin=data.get('codigo_pin', ''),
        numero_checkin=data.get('numero_checkin', '')
    )
    
    db.session.add(alojamiento)
    db.session.commit()
    
    return jsonify({'success': True, 'alojamiento_id': alojamiento.id})
