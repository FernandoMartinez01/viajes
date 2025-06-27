# -*- coding: utf-8 -*-
"""
Blueprint para rutas de transportes.
"""

from flask import Blueprint, request, jsonify

# Crear el blueprint
transportes_bp = Blueprint('transportes', __name__)

# Variables globales para servicios (se inicializarán después)
transporte_service = None

def init_transportes_routes(models_dict, database_instance, services_dict):
    """Inicializa las rutas de transportes con los servicios necesarios."""
    global transporte_service
    
    transporte_service = services_dict['transporte_service']

@transportes_bp.route('/viaje/<int:viaje_id>/transporte', methods=['POST'])
def agregar_transporte(viaje_id):
    """Agregar un nuevo transporte a un viaje."""
    data = request.get_json()
    
    resultado = transporte_service.crear_transporte(
        viaje_id=viaje_id,
        tipo=data.get('tipo', 'vuelo'),
        origen=data['origen'],
        destino=data['destino'],
        fecha_salida=data['fecha_salida'],
        fecha_llegada=data['fecha_llegada'],
        hora_salida=data.get('hora_salida'),
        hora_llegada=data.get('hora_llegada'),
        codigo_reserva=data.get('codigo_reserva', ''),
        aerolinea=data.get('aerolinea', ''),
        numero_vuelo=data.get('numero_vuelo', ''),
        terminal=data.get('terminal', ''),
        puerta=data.get('puerta', ''),
        asiento=data.get('asiento', ''),
        notas=data.get('notas', '')
    )
    
    return jsonify(resultado)
