# -*- coding: utf-8 -*-
"""
Blueprint para rutas de documentos.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

# Crear el blueprint
documentos_bp = Blueprint('documentos', __name__)

# Variables globales para modelos y funciones (se inicializarán después)
Documento = None
db = None

def init_documentos_routes(models_dict, database_instance):
    """Inicializa las rutas de documentos con los modelos y base de datos necesarios."""
    global Documento, db
    
    Documento = models_dict['Documento']
    db = database_instance

@documentos_bp.route('/viaje/<int:viaje_id>/documento', methods=['POST'])
def agregar_documento(viaje_id):
    """Agregar un nuevo documento a un viaje."""
    data = request.get_json()
    
    documento = Documento(
        viaje_id=viaje_id,
        tipo=data['tipo'],
        nombre=data['nombre'],
        numero=data.get('numero', ''),
        fecha_vencimiento=datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date() if data.get('fecha_vencimiento') else None,
        notas=data.get('notas', '')
    )
    
    db.session.add(documento)
    db.session.commit()
    
    return jsonify({'success': True, 'documento_id': documento.id})
