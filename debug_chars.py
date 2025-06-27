#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script para detectar caracteres problemáticos en index.html

with open('templates/index.html', 'rb') as f:
    content = f.read()

print("=== ANÁLISIS DE CARACTERES EN INDEX.HTML ===")

# Buscar todas las ocurrencias del carácter '>'
for i, byte in enumerate(content):
    if chr(byte) == '>':
        # Mostrar contexto alrededor del carácter
        start = max(0, i-20)
        end = min(len(content), i+21)
        context = content[start:end].decode('utf-8', errors='replace')
        print(f"'>' encontrado en posición {i}:")
        print(f"  Contexto: {repr(context)}")
        print(f"  Línea aprox: {content[:i].count(b'\\n') + 1}")
        print()

# También buscar caracteres no ASCII
print("\n=== CARACTERES NO ASCII ===")
for i, byte in enumerate(content):
    if byte > 127:
        char = chr(byte) if byte < 256 else '?'
        print(f"Carácter no-ASCII en posición {i}: {byte} ('{char}')")
        if i < 2000:  # Solo mostrar los primeros para no saturar
            start = max(0, i-10)
            end = min(len(content), i+11)
            context = content[start:end].decode('utf-8', errors='replace')
            print(f"  Contexto: {repr(context)}")
