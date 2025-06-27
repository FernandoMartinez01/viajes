#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script para debugging de los datos de viajes

import sqlite3
import os

# Ruta a la base de datos
db_path = os.path.join(os.path.expanduser('~'), 'Documents', 'viaje_local', 'viaje.db')

print(f"Conectando a base de datos: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtener todos los viajes
    cursor.execute("SELECT id, nombre, fecha_inicio, fecha_fin FROM viaje ORDER BY fecha_inicio DESC")
    viajes = cursor.fetchall()
    
    print("\n=== DEBUG VIAJES (desde SQLite) ===")
    
    for i, (viaje_id, nombre, fecha_inicio, fecha_fin) in enumerate(viajes):
        print(f"\nViaje {i+1}:")
        print(f"  ID: {viaje_id}")
        print(f"  Nombre: '{nombre}'")
        print(f"  Nombre (repr): {repr(nombre)}")
        print(f"  Tipo nombre: {type(nombre)}")
        
        # Verificar si hay caracteres especiales
        if nombre:
            for j, char in enumerate(nombre):
                if ord(char) > 127 or char in ['>', '<', '"', "'", "&"]:
                    print(f"    Carácter especial en posición {j}: '{char}' (ord: {ord(char)})")
        
        print(f"  Fecha inicio: {fecha_inicio}")
        print(f"  Fecha fin: {fecha_fin}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
