#!/usr/bin/env python3
"""
Script para inicializar la base de datos en producción
"""
import os
import sys
from app import app, db

def init_db():
    """Crear todas las tablas de la base de datos"""
    with app.app_context():
        print("Creando tablas de base de datos...")
        db.create_all()
        print("✅ Base de datos inicializada correctamente!")

def reset_db():
    """Eliminar y recrear todas las tablas (¡CUIDADO!)"""
    with app.app_context():
        print("⚠️  ELIMINANDO todas las tablas...")
        db.drop_all()
        print("Recreando tablas...")
        db.create_all()
        print("✅ Base de datos reinicializada!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        confirm = input("¿Estás seguro de que quieres ELIMINAR todos los datos? (escriba 'SI'): ")
        if confirm == 'SI':
            reset_db()
        else:
            print("Operación cancelada.")
    else:
        init_db()
