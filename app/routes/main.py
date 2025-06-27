# -*- coding: utf-8 -*-
"""
Blueprint para rutas principales de la aplicación.
"""

from flask import Blueprint, render_template, jsonify
from datetime import datetime, date

# Crear el blueprint
main_bp = Blueprint('main', __name__)

# Importar funciones y modelos necesarios (se definirán después de la inicialización)
Viaje = None
ensure_db_initialized = None
init_db_auto = None
get_db_initialized_status = None
set_db_initialized_status = None

def init_main_routes(models_dict, db_functions):
    """Inicializa las rutas principales con los modelos y funciones necesarias."""
    global Viaje, ensure_db_initialized, init_db_auto, get_db_initialized_status, set_db_initialized_status
    
    Viaje = models_dict['Viaje']
    ensure_db_initialized = db_functions['ensure_db_initialized']
    init_db_auto = db_functions['init_db_auto']
    get_db_initialized_status = db_functions['get_db_initialized_status']
    set_db_initialized_status = db_functions['set_db_initialized_status']

@main_bp.route('/')
def index():
    """Página principal con lista de viajes."""
    # Asegurar que la DB esté inicializada
    ensure_db_initialized()
    
    # Asegurar que la DB esté inicializada (failsafe)
    try:
        viajes = Viaje.query.order_by(Viaje.fecha_inicio.desc()).all()
    except Exception as e:
        print(f"Error de BD, intentando inicializar: {e}")
        init_db_auto()
        viajes = Viaje.query.order_by(Viaje.fecha_inicio.desc()).all()
    
    return render_template('index.html', viajes=viajes, hoy=date.today())

@main_bp.route('/health')
def health_check():
    """Endpoint de health check para Railway y otros servicios."""
    try:
        # Asegurar que la DB esté inicializada
        ensure_db_initialized()
        
        # Verificar que la app y la DB están funcionando
        viajes_count = Viaje.query.count()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'viajes': viajes_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        print(f"❌ Health check falló: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@main_bp.route('/init-db')
def force_init_db():
    """Endpoint temporal para inicializar DB manualmente."""
    try:
        set_db_initialized_status(False)  # Forzar re-inicialización
        
        success = init_db_auto()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Base de datos inicializada correctamente',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error al inicializar base de datos',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Manejadores de errores
@main_bp.errorhandler(500)
def internal_error(error):
    """Manejador de errores internos del servidor."""
    print(f"Error 500: {error}")
    import traceback
    traceback.print_exc()
    
    # Importar db dinámicamente para evitar problemas de inicialización
    from app.models import db
    if db:
        db.session.rollback()
    
    return jsonify({
        'error': 'Error interno del servidor',
        'message': 'Ha ocurrido un error inesperado'
    }), 500

@main_bp.errorhandler(404)
def not_found(error):
    """Manejador de errores 404."""
    return jsonify({
        'error': 'No encontrado',
        'message': 'El recurso solicitado no existe'
    }), 404
