# -*- coding: utf-8 -*-
"""
Blueprint para rutas de alojamientos.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

# Crear el blueprint
alojamientos_bp = Blueprint('alojamientos', __name__)

# Variables globales para servicios (se inicializarán después)
alojamiento_service = None

def init_alojamientos_routes(alojamiento_service_instance):
    """Inicializa las rutas de alojamientos con el servicio necesario."""
    global alojamiento_service
    
    alojamiento_service = alojamiento_service_instance

@alojamientos_bp.route('/viaje/<int:viaje_id>/alojamiento', methods=['POST'])
def agregar_alojamiento(viaje_id):
    """Agregar un nuevo alojamiento a un viaje."""
    if not alojamiento_service:
        return jsonify({'success': False, 'error': 'Servicio no inicializado'}), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        # Validar campos requeridos
        campos_requeridos = ['nombre', 'destino', 'direccion', 'fecha_entrada', 'fecha_salida']
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                return jsonify({'success': False, 'error': f'Campo requerido: {campo}'}), 400
        
        resultado = alojamiento_service.crear_alojamiento(
            viaje_id=viaje_id,
            nombre=data['nombre'],
            destino=data['destino'],
            direccion=data['direccion'],
            fecha_entrada=data['fecha_entrada'],
            fecha_salida=data['fecha_salida'],
            horario_checkin=data.get('horario_checkin', '15:00'),
            horario_checkout=data.get('horario_checkout', '11:00'),
            incluye_desayuno=data.get('incluye_desayuno', False),
            numero_confirmacion=data.get('numero_confirmacion', ''),
            codigo_pin=data.get('codigo_pin', ''),
            numero_checkin=data.get('numero_checkin', '')
        )
        
        if resultado['success']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
