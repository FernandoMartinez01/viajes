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
    
    print("✅ Blueprints registrados correctamente")

# Exportar función principal
__all__ = ['register_blueprints']
