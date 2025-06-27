# -*- coding: utf-8 -*-
"""
Blueprint para rutas de gastos.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

# Crear el blueprint
gastos_bp = Blueprint('gastos', __name__)

# Variables globales para modelos y funciones (se inicializarán después)
Gasto = None
Viaje = None
db = None

def init_gastos_routes(models_dict, database_instance):
    """Inicializa las rutas de gastos con los modelos y base de datos necesarios."""
    global Gasto, Viaje, db
    
    Gasto = models_dict['Gasto']
    Viaje = models_dict['Viaje']
    db = database_instance

@gastos_bp.route('/viaje/<int:viaje_id>/gasto', methods=['POST'])
def agregar_gasto(viaje_id):
    """Agregar un nuevo gasto a un viaje."""
    data = request.get_json()
    
    gasto = Gasto(
        viaje_id=viaje_id,
        categoria=data['categoria'],
        descripcion=data['descripcion'],
        monto=float(data['monto']),
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        moneda=data.get('moneda', 'USD')
    )
    
    db.session.add(gasto)
    db.session.flush()  # Para que el gasto esté disponible en la relación
    
    # Actualizar presupuesto gastado - solo suma todos los gastos del viaje
    viaje = Viaje.query.get(viaje_id)
    viaje.presupuesto_gastado = sum(g.monto for g in viaje.gastos)
    
    db.session.commit()
    
    return jsonify({'success': True, 'gasto_id': gasto.id})
