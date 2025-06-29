"""
Versión simplificada de app.py para Railway
Con mejor manejo de errores y logging
"""

import os
import sys
from flask import Flask, jsonify
from datetime import datetime

# Crear app básica primero
app = Flask(__name__)

# Configuración mínima
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')

# Health check súper simple que siempre funciona
@app.route('/ping')
def ping():
    return jsonify({
        'status': 'ok',
        'message': 'pong',
        'timestamp': datetime.utcnow().isoformat(),
        'python_version': sys.version
    }), 200

@app.route('/health')  
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/status')
def status():
    global app_loaded
    return jsonify({
        'app_loaded': app_loaded,
        'status': 'complete' if app_loaded else 'loading',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/')
def home():
    return jsonify({
        'message': 'Viajes PWA - Cargando...',
        'status': 'loading',
        'timestamp': datetime.utcnow().isoformat(),
        'note': 'App completa se está cargando en segundo plano'
    })

# Variable para indicar si la app completa está lista
app_loaded = False

# Intentar cargar la app completa solo si es posible
try:
    print("🔄 Intentando cargar configuración completa...")
    
    # Solo importar si las dependencias están disponibles
    from config.settings import Config
    
    # Configuración usando el módulo separado
    app.config['SECRET_KEY'] = Config.get_secret_key()
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.get_sqlalchemy_track_modifications()
    
    print("✅ Configuración cargada")
    
    # Intentar inicializar base de datos
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
    
    print("✅ SQLAlchemy inicializado")
    
    # Intentar cargar modelos
    from app.models import init_models
    models = init_models(db)
    
    print("✅ Modelos cargados")
    
    # Intentar cargar servicios
    from app.services import database_service, viaje_service, gasto_service, actividad_service, documento_service, transporte_service, alojamiento_service
    
    # Inicializar servicios
    database_service.init_service(app, db, models)
    viaje_service.init_service(models, db)
    gasto_service.init_models(models, db)
    actividad_service.init_models(models, db)
    documento_service.init_models(models, db)
    transporte_service.init_models(models, db)
    alojamiento_service.init_models(models, db)
    
    print("✅ Servicios inicializados")
    
    # Cargar blueprints
    def init_blueprints_dependencies():
        db_functions = {
            'ensure_db_initialized': database_service.ensure_initialized,
            'init_db_auto': database_service.init_database,
            'get_db_initialized_status': lambda: database_service.is_initialized,
            'set_db_initialized_status': database_service.set_initialized
        }
        
        from app.routes.main import init_main_routes
        init_main_routes(models, db_functions)
        
        from app.routes.viajes import init_viajes_routes
        init_viajes_routes(models, db)
        
        from app.routes.gastos import init_gastos_routes
        init_gastos_routes(gasto_service)
        
        from app.routes.actividades import init_actividades_routes
        init_actividades_routes(actividad_service)
        
        from app.routes.documentos import init_documentos_routes
        init_documentos_routes(documento_service)
        
        from app.routes.transportes import init_transportes_routes
        services_dict = {'transporte_service': transporte_service}
        init_transportes_routes(models, db, services_dict)
        
        from app.routes.alojamientos import init_alojamientos_routes
        init_alojamientos_routes(alojamiento_service)
    
    init_blueprints_dependencies()
    
    # Registrar blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    print("✅ Blueprints registrados")
    
    # Headers de respuesta para desarrollo
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
        response.headers.add('Pragma', 'no-cache')
        response.headers.add('Expires', '0')
        return response
    
    # Actualizar ruta home para app completa
    @app.route('/')
    def home_full():
        try:
            from app.routes.main import index
            return index()
        except Exception as e:
            print(f"Error en ruta principal: {e}")
            return jsonify({
                'error': 'Error cargando página principal',
                'message': str(e),
                'fallback': True
            })
    
    print("✅ App completa cargada exitosamente")
    app_loaded = True
    
except Exception as e:
    print(f"⚠️ No se pudo cargar la app completa: {e}")
    print("🔄 Continuando con versión simplificada...")
    import traceback
    traceback.print_exc()
    app_loaded = False

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Iniciando servidor en puerto {port}")
    print(f"🔧 Modo debug: {debug_mode}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
