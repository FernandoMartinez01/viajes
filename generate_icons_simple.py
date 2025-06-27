#!/usr/bin/env python3
"""
Script para generar iconos PWA básicos usando solo Pillow.
Crea iconos simples pero efectivos para la aplicación de viajes.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Tamaños de iconos requeridos para PWA
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def create_travel_icon(size):
    """Crea un icono de viaje simple usando formas básicas"""
    # Crear imagen con fondo transparente
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colores de la app
    bg_color = '#2196F3'
    white = '#FFFFFF'
    accent = '#FF9800'
    dark_blue = '#1976D2'
    
    # Dibujar fondo circular
    margin = size * 0.05
    draw.ellipse([margin, margin, size-margin, size-margin], fill=bg_color)
    
    # Calcular dimensiones de la maleta
    suitcase_width = size * 0.4
    suitcase_height = size * 0.3
    suitcase_x = (size - suitcase_width) / 2
    suitcase_y = size * 0.35
    
    # Dibujar maleta principal
    draw.rectangle([
        suitcase_x, suitcase_y,
        suitcase_x + suitcase_width, suitcase_y + suitcase_height
    ], fill=white, outline=dark_blue, width=max(1, size//64))
    
    # Dibujar asa de la maleta
    handle_width = suitcase_width * 0.3
    handle_height = size * 0.08
    handle_x = suitcase_x + (suitcase_width - handle_width) / 2
    handle_y = suitcase_y - handle_height / 2
    
    draw.rectangle([
        handle_x, handle_y,
        handle_x + handle_width, handle_y + handle_height
    ], outline=dark_blue, width=max(1, size//64))
    
    # Dibujar líneas decorativas en la maleta
    line_spacing = suitcase_height / 6
    line_width = max(1, size//128)
    for i in range(1, 5):
        y = suitcase_y + i * line_spacing
        draw.line([
            suitcase_x + suitcase_width * 0.1, y,
            suitcase_x + suitcase_width * 0.9, y
        ], fill=dark_blue, width=line_width)
    
    # Dibujar cerraduras
    lock_size = max(2, size//32)
    lock_height = max(4, size//16)
    
    # Cerradura izquierda
    draw.rectangle([
        suitcase_x + suitcase_width * 0.15, suitcase_y + suitcase_height * 0.2,
        suitcase_x + suitcase_width * 0.15 + lock_size, suitcase_y + suitcase_height * 0.2 + lock_height
    ], fill=accent)
    
    # Cerradura derecha
    draw.rectangle([
        suitcase_x + suitcase_width * 0.85 - lock_size, suitcase_y + suitcase_height * 0.2,
        suitcase_x + suitcase_width * 0.85, suitcase_y + suitcase_height * 0.2 + lock_height
    ], fill=accent)
    
    # Dibujar avión pequeño (símbolo de viaje)
    plane_size = size * 0.15
    plane_x = size * 0.7
    plane_y = size * 0.7
    
    # Cuerpo del avión
    draw.ellipse([
        plane_x, plane_y,
        plane_x + plane_size * 0.8, plane_y + plane_size * 0.3
    ], fill=white)
    
    # Alas del avión
    draw.ellipse([
        plane_x + plane_size * 0.2, plane_y - plane_size * 0.1,
        plane_x + plane_size * 0.6, plane_y + plane_size * 0.4
    ], fill=white)
    
    return img

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, 'static', 'icons')
    
    # Crear directorio si no existe
    os.makedirs(icons_dir, exist_ok=True)
    
    print("Generando iconos PWA con Pillow...")
    
    for size in ICON_SIZES:
        try:
            # Generar icono
            icon = create_travel_icon(size)
            
            # Guardar
            output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
            icon.save(output_path, 'PNG')
            print(f"✓ Generado: icon-{size}x{size}.png")
            
        except Exception as e:
            print(f"✗ Error generando icon-{size}x{size}.png: {e}")
    
    print("\n¡Iconos generados exitosamente!")
    print(f"Iconos guardados en: {icons_dir}")

if __name__ == "__main__":
    main()
