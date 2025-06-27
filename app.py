import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from config.settings import Config
from app.utils.helpers import porcentaje_presupuesto

app = Flask(__name__)

# Configuración usando el módulo separado
app.config['SECRET_KEY'] = Config.get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.get_sqlalchemy_track_modifications()

db = SQLAlchemy(app)

# Inicializar modelos y obtener las clases
from app.models import init_models
models = init_models(db)

# Asignar modelos a variables globales para fácil acceso
Viaje = models['Viaje']
Parada = models['Parada']
Gasto = models['Gasto']
Actividad = models['Actividad']
Documento = models['Documento']
Transporte = models['Transporte']
Alojamiento = models['Alojamiento']

# Inicializar servicios de negocio
from app.services import database_service, viaje_service, gasto_service, actividad_service, documento_service
database_service.init_service(app, db, models)
viaje_service.init_service(models, db)
gasto_service.init_models(models, db)
actividad_service.init_models(models, db)
documento_service.init_models(models, db)
print("🧳 GastoService inicializado")
print("🎯 ActividadService inicializado")
print("📄 DocumentoService inicializado")

# Función para inicializar blueprints con dependencias
def init_blueprints_dependencies():
    """Inicializa los blueprints con sus dependencias necesarias."""
    # Preparar funciones para las rutas principales usando el servicio de DB
    db_functions = {
        'ensure_db_initialized': database_service.ensure_initialized,
        'init_db_auto': database_service.init_database,
        'get_db_initialized_status': lambda: database_service.is_initialized,
        'set_db_initialized_status': database_service.set_initialized
    }
    
    # Inicializar rutas principales
    from app.routes.main import init_main_routes
    init_main_routes(models, db_functions)
    
    # Inicializar rutas de viajes
    from app.routes.viajes import init_viajes_routes
    init_viajes_routes(models, db)
    
    # Inicializar rutas de gastos
    from app.routes.gastos import init_gastos_routes
    init_gastos_routes(gasto_service)
    
    # Inicializar rutas de actividades
    from app.routes.actividades import init_actividades_routes
    init_actividades_routes(actividad_service)
    
    # Inicializar rutas de documentos
    from app.routes.documentos import init_documentos_routes
    init_documentos_routes(documento_service)
    
    # Inicializar rutas de transportes
    from app.routes.transportes import init_transportes_routes
    init_transportes_routes(models, db)
    
    # Inicializar rutas de alojamientos
    from app.routes.alojamientos import init_alojamientos_routes
    init_alojamientos_routes(models, db)

# Inicializar blueprints con sus dependencias ANTES de registrarlos
init_blueprints_dependencies()

# Registrar blueprints
from app.routes import register_blueprints
register_blueprints(app)

# Variable global para controlar la inicialización
# Funciones de base de datos movidas a app/services/database.py

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

# Modelos de base de datos importados desde app.models

# Rutas principales movidas a app/routes/main.py

# Rutas de viajes movidas a app/routes/viajes.py

# Rutas de eliminación de viajes movidas a app/routes/viajes.py

# Ruta de nuevo viaje movida a app/routes/viajes.py

# Ruta de gastos movida a app/routes/gastos.py

# Ruta de actividades movida a app/routes/actividades.py

# Rutas de documentos movidas a app/routes/documentos.py

# Rutas de transportes movidas a app/routes/transportes.py

# Rutas de alojamientos movidas a app/routes/alojamientos.py

# Rutas de paradas movidas a app/routes/viajes.py

# Ruta de completar actividad movida a app/routes/actividades.py

# Registrar función helper como filtro de template
app.template_filter('porcentaje_presupuesto')(porcentaje_presupuesto)

# Crear tablas automáticamente en el primer acceso (función legacy)
def init_db():
    return database_service.init_database()

# Rutas de health check y init-db movidas a app/routes/main.py

# Manejadores de errores movidos a app/routes/main.py

if __name__ == '__main__':
    # Inicializar base de datos
    if not init_db():
        print("⚠️  Continuando sin inicialización de DB...")
    
    # Para desarrollo local y producción
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Iniciando servidor en puerto {port}")
    print(f"🔧 Modo debug: {debug_mode}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
