# -*- coding: utf-8 -*-
"""
Blueprint para rutas de documentos.
"""

from flask import Blueprint, request, jsonify

# Crear el blueprint
documentos_bp = Blueprint('documentos', __name__)

# Variables globales para servicios (se inicializarán después)
documento_service = None

def init_documentos_routes(documento_service_instance):
    """Inicializa las rutas de documentos con el servicio necesario."""
    global documento_service
    documento_service = documento_service_instance

@documentos_bp.route('/viaje/<int:viaje_id>/documento', methods=['POST'])
def agregar_documento(viaje_id):
    """Agregar un nuevo documento a un viaje."""
    data = request.get_json()
    
    resultado = documento_service.crear_documento(
        viaje_id=viaje_id,
        tipo=data['tipo'],
        nombre=data['nombre'],
        numero=data.get('numero', ''),
        fecha_vencimiento=data.get('fecha_vencimiento'),
        notas=data.get('notas', '')
    )
    
    return jsonify(resultado)

@documentos_bp.route('/viaje/<int:viaje_id>/documentos/validar', methods=['GET'])
def validar_documentos(viaje_id):
    """Validar documentos esenciales para un viaje."""
    resultado = documento_service.validar_documentos_para_viaje(viaje_id)
    return jsonify(resultado)

@documentos_bp.route('/viaje/<int:viaje_id>/documentos/vencimientos', methods=['GET'])
def verificar_vencimientos(viaje_id):
    """Verificar documentos próximos a vencer."""
    dias = request.args.get('dias', 30, type=int)
    resultado = documento_service.verificar_vencimientos(viaje_id, dias)
    return jsonify(resultado)

@documentos_bp.route('/viaje/<int:viaje_id>/documentos/estadisticas', methods=['GET'])
def estadisticas_documentos(viaje_id):
    """Obtener estadísticas de documentos de un viaje."""
    resultado = documento_service.obtener_estadisticas_documentos(viaje_id)
    return jsonify(resultado)
