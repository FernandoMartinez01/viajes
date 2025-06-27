# -*- coding: utf-8 -*-
"""
Blueprint para rutas de gastos.
"""

from flask import Blueprint, request, jsonify

# Crear el blueprint
gastos_bp = Blueprint('gastos', __name__)

# Variables globales para modelos y servicios (se inicializarán después)
gasto_service = None

def init_gastos_routes(gasto_service_instance):
    """Inicializa las rutas de gastos con el servicio necesario."""
    global gasto_service
    gasto_service = gasto_service_instance

@gastos_bp.route('/viaje/<int:viaje_id>/gasto', methods=['POST'])
def agregar_gasto(viaje_id):
    """Agregar un nuevo gasto a un viaje."""
    data = request.get_json()
    
    resultado = gasto_service.crear_gasto(
        viaje_id=viaje_id,
        categoria=data['categoria'],
        descripcion=data['descripcion'],
        monto=data['monto'],
        fecha=data['fecha'],
        moneda=data.get('moneda', 'USD')
    )
    
    return jsonify(resultado)
