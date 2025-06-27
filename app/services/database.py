# -*- coding: utf-8 -*-
"""
Servicio para manejo de base de datos.
"""

import os


class DatabaseService:
    """Servicio centralizado para operaciones de base de datos."""
    
    def __init__(self):
        self._db = None
        self._app = None
        self._models = None
        self._initialized = False
    
    def init_service(self, app, db, models):
        """Inicializa el servicio con la aplicación, base de datos y modelos."""
        self._app = app
        self._db = db
        self._models = models
        print("🔧 DatabaseService inicializado")
    
    @property
    def is_initialized(self):
        """Retorna si la base de datos está inicializada."""
        return self._initialized
    
    def set_initialized(self, status):
        """Establece el estado de inicialización."""
        self._initialized = status
    
    def init_database(self):
        """Inicializa la base de datos automáticamente."""
        if self._initialized:
            return True
            
        try:
            print("🔄 Inicializando base de datos...")
            
            # Crear el directorio si no existe (solo para SQLite local)
            db_uri = self._app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                    print(f"📁 Directorio de DB creado: {db_dir}")
            
            # Usar contexto de aplicación para crear tablas
            with self._app.app_context():
                self._db.create_all()
                print("✅ Tablas de base de datos verificadas/creadas correctamente")
                
                # Verificar que la conexión funciona
                Viaje = self._models['Viaje']
                viajes_count = Viaje.query.count()
                print(f"📊 Base de datos conectada correctamente. Viajes existentes: {viajes_count}")
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Error al crear tablas: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def ensure_initialized(self):
        """Garantiza que la DB esté inicializada antes de cualquier operación."""
        if not self._initialized:
            self.init_database()
    
    def get_status(self):
        """Retorna el estado actual de la base de datos."""
        return {
            'initialized': self._initialized,
            'uri': self._app.config.get('SQLALCHEMY_DATABASE_URI', 'No configurada') if self._app else 'App no inicializada',
            'models_loaded': len(self._models) if self._models else 0
        }


# Instancia global del servicio
database_service = DatabaseService()
