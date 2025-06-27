"""
Configuración para la aplicación de viajes
==========================================
"""

import os

class Config:
    """Configuración base extraída de app.py"""
    
    @staticmethod
    def get_secret_key():
        return os.environ.get('SECRET_KEY', 'tu-clave-secreta-aqui')
    
    @staticmethod
    def get_database_uri():
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # Producción (PostgreSQL) - Corregir URL si es necesario
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        else:
            # Desarrollo (SQLite) - Usar ruta local fuera de OneDrive
            local_db_path = os.path.join(os.path.expanduser('~'), 'Documents', 'viaje_local', 'viaje.db')
            print(f"🗄️  Usando SQLite en desarrollo: {local_db_path}")
            return f'sqlite:///{local_db_path}'
    
    @staticmethod
    def get_sqlalchemy_track_modifications():
        return False
