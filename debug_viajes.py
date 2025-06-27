#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ejecutar app.py directamente para inicializar todo
exec(open('app.py').read())

# Los modelos deberían estar disponibles ahora
print("=== DEBUG VIAJES ===")
viajes = Viaje.query.all()

for i, viaje in enumerate(viajes):
    print(f"\nViaje {i+1}:")
    print(f"  ID: {viaje.id}")
    print(f"  Nombre: '{viaje.nombre}'")
    print(f"  Nombre (repr): {repr(viaje.nombre)}")
    print(f"  Tipo nombre: {type(viaje.nombre)}")
    
    # Verificar si hay caracteres especiales
    if viaje.nombre:
        for j, char in enumerate(viaje.nombre):
            if ord(char) > 127 or char in ['>', '<', '"', "'"]:
                print(f"    Carácter especial en posición {j}: '{char}' (ord: {ord(char)})")
    
    print(f"  Fecha inicio: {viaje.fecha_inicio}")
    print(f"  Fecha fin: {viaje.fecha_fin}")
