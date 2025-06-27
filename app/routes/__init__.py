# -*- coding: utf-8 -*-
"""
Módulo de rutas y blueprints para la aplicación de viajes.
"""

def register_blueprints(app):
    """Registra todos los blueprints en la aplicación Flask."""
    
    # Importar y registrar blueprint de rutas principales
    from .main import main_bp
    app.register_blueprint(main_bp)
    
    # Importar y registrar blueprint de viajes
    from .viajes import viajes_bp
    app.register_blueprint(viajes_bp)
    
    # Importar y registrar blueprint de gastos
    from .gastos import gastos_bp
    app.register_blueprint(gastos_bp)
    
    # Importar y registrar blueprint de actividades
    from .actividades import actividades_bp
    app.register_blueprint(actividades_bp)
    
    # Importar y registrar blueprint de documentos
    from .documentos import documentos_bp
    app.register_blueprint(documentos_bp)
    
    # Importar y registrar blueprint de transportes
    from .transportes import transportes_bp
    app.register_blueprint(transportes_bp)
    
    # Importar y registrar blueprint de alojamientos
    from .alojamientos import alojamientos_bp
    app.register_blueprint(alojamientos_bp)
    
    print("✅ Blueprints registrados correctamente")

# Exportar función principal
__all__ = ['register_blueprints']
