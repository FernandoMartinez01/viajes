# Iconos PWA - Mi Viaje

✅ **COMPLETADO** - Los iconos PWA ya están generados y configurados.

## Iconos Disponibles

Los siguientes iconos han sido generados automáticamente:

- `icon-72x72.png` - Para dispositivos iOS y Android básicos
- `icon-96x96.png` - Para Chrome y Android
- `icon-128x128.png` - Para aplicaciones web y Chrome
- `icon-144x144.png` - Para Windows tiles y Android
- `icon-152x152.png` - Para iPad
- `icon-192x192.png` - Para Android home screen
- `icon-384x384.png` - Para splash screens
- `icon-512x512.png` - Para PWA y splash screens grandes

## Diseño

Los iconos presentan:
- 🧳 Una maleta de viaje como elemento principal
- ✈️ Un pequeño avión como símbolo de viaje  
- 🎨 Colores corporativos: azul (#2196F3) y naranja (#FF9800)
- 📱 Diseño optimizado para visualización en dispositivos móviles

## Regeneración

Si necesitas regenerar los iconos:

```bash
python generate_icons_simple.py
```

O para una versión más avanzada (requiere cairocffi):

```bash
python generate_icons.py
```

## Archivo Base

El archivo `icon-base.svg` contiene el diseño vectorial base que se usa para generar todos los tamaños.
