# -*- coding: utf-8 -*-
"""
Modelos de base de datos para la aplicación de viajes.
"""

# La instancia db se inicializa externamente e importada aquí
db = None

def init_models(database_instance):
    """Inicializa los modelos con la instancia de base de datos."""
    global db
    db = database_instance
    
    # Ahora podemos importar los modelos de forma segura
    from .viaje import Viaje, Parada
    from .gasto import Gasto
    from .actividad import Actividad
    from .documento import Documento
    from .transporte import Transporte
    from .alojamiento import Alojamiento
    
    return {
        'Viaje': Viaje,
        'Parada': Parada,
        'Gasto': Gasto,
        'Actividad': Actividad,
        'Documento': Documento,
        'Transporte': Transporte,
        'Alojamiento': Alojamiento
    }

# Exportar para fácil importación
__all__ = [
    'db',
    'init_models'
]
