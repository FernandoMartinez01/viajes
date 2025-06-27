"""
Funciones auxiliares para la aplicación de viajes
"""

def porcentaje_presupuesto(gastado, total):
    """Calcula el porcentaje de presupuesto gastado"""
    if total <= 0:
        return 0
    return min(100, (gastado / total) * 100)
