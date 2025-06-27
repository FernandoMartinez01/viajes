# -*- coding: utf-8 -*-
"""
Blueprint para rutas de transportes.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

# Crear el blueprint
transportes_bp = Blueprint('transportes', __name__)

# Variables globales para modelos y funciones (se inicializarán después)
Transporte = None
db = None

def init_transportes_routes(models_dict, database_instance):
    """Inicializa las rutas de transportes con los modelos y base de datos necesarios."""
    global Transporte, db
    
    Transporte = models_dict['Transporte']
    db = database_instance

@transportes_bp.route('/viaje/<int:viaje_id>/transporte', methods=['POST'])
def agregar_transporte(viaje_id):
    """Agregar un nuevo transporte a un viaje."""
    data = request.get_json()
    
    transporte = Transporte(
        viaje_id=viaje_id,
        tipo=data.get('tipo', 'vuelo'),
        origen=data['origen'],
        destino=data['destino'],
        codigo_reserva=data.get('codigo_reserva', ''),
        fecha_salida=datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date(),
        hora_salida=datetime.strptime(data['hora_salida'], '%H:%M').time() if data.get('hora_salida') else None,
        fecha_llegada=datetime.strptime(data['fecha_llegada'], '%Y-%m-%d').date(),
        hora_llegada=datetime.strptime(data['hora_llegada'], '%H:%M').time() if data.get('hora_llegada') else None,
        aerolinea=data.get('aerolinea', ''),
        numero_vuelo=data.get('numero_vuelo', ''),
        terminal=data.get('terminal', ''),
        puerta=data.get('puerta', ''),
        asiento=data.get('asiento', ''),
        notas=data.get('notas', '')
    )
    
    db.session.add(transporte)
    db.session.commit()
    
    return jsonify({'success': True, 'transporte_id': transporte.id})
