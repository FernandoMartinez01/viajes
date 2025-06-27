#!/usr/bin/env python3
"""
Script para generar iconos PWA en diferentes tamaños desde un SVG base.
Requiere: pip install Pillow cairosvg
"""

import os
from PIL import Image
import cairosvg
import io

# Tamaños de iconos requeridos para PWA
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def generate_icon(svg_content, size):
    """Genera un icono PNG de un tamaño específico desde contenido SVG"""
    # Convertir SVG a PNG usando cairosvg
    png_data = cairosvg.svg2png(
        bytestring=svg_content.encode('utf-8'),
        output_width=size,
        output_height=size
    )
    
    # Cargar con PIL para cualquier post-procesamiento si es necesario
    image = Image.open(io.BytesIO(png_data))
    return image

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = script_dir
    svg_path = os.path.join(icons_dir, 'icon-base.svg')
    
    if not os.path.exists(svg_path):
        print(f"Error: No se encontró {svg_path}")
        return
    
    # Leer el SVG base
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    print("Generando iconos PWA...")
    
    for size in ICON_SIZES:
        try:
            # Generar icono
            icon = generate_icon(svg_content, size)
            
            # Guardar
            output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
            icon.save(output_path, 'PNG')
            print(f"✓ Generado: icon-{size}x{size}.png")
            
        except Exception as e:
            print(f"✗ Error generando icon-{size}x{size}.png: {e}")
    
    print("\n¡Iconos generados exitosamente!")
    print("\nRecuerda instalar las dependencias si no las tienes:")
    print("pip install Pillow cairosvg")

if __name__ == "__main__":
    main()
