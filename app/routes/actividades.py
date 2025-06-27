# -*- coding: utf-8 -*-
"""
Blueprint para rutas de actividades.
"""

from flask import Blueprint, request, jsonify

# Crear el blueprint
actividades_bp = Blueprint('actividades', __name__)

# Variables globales para servicios (se inicializarán después)
actividad_service = None

def init_actividades_routes(actividad_service_instance):
    """Inicializa las rutas de actividades con el servicio necesario."""
    global actividad_service
    actividad_service = actividad_service_instance

@actividades_bp.route('/viaje/<int:viaje_id>/actividad', methods=['POST'])
def agregar_actividad(viaje_id):
    """Agregar una nueva actividad a un viaje."""
    data = request.get_json()
    
    resultado = actividad_service.crear_actividad(
        viaje_id=viaje_id,
        nombre=data['nombre'],
        fecha=data['fecha'],
        destino=data.get('destino', 'general'),
        hora=data.get('hora'),
        ubicacion=data.get('ubicacion', ''),
        descripcion=data.get('descripcion', '')
    )
    
    return jsonify(resultado)

@actividades_bp.route('/actividad/<int:actividad_id>/completar', methods=['POST'])
def completar_actividad(actividad_id):
    """Marcar una actividad como completada o no completada."""
    resultado = actividad_service.completar_actividad(actividad_id)
    return jsonify(resultado)
