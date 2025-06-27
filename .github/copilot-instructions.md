# Instrucciones para GitHub Copilot

Esta es una aplicación web progresiva (PWA) para control de viajes construida con Python Flask y optimizada para dispositivos móviles.

## Contexto del Proyecto

- **Objetivo**: App móvil para controlar todos los aspectos de un viaje
- **Tecnologías**: Python Flask, HTML5, CSS3, JavaScript, SQLite
- **Características**: PWA, diseño mobile-first, modo offline, instalable

## Arquitectura

### Backend (Flask)
- `app.py`: Aplicación principal con rutas y modelos SQLAlchemy
- Modelos: Viaje, Gasto, Actividad, Documento
- Base de datos: SQLite para desarrollo, PostgreSQL para producción

### Frontend
- Diseño mobile-first con Material Design
- PWA con Service Worker para funcionalidad offline
- JavaScript vanilla para interactividad
- CSS Grid y Flexbox para layouts responsivos

### Estructura de archivos
- `templates/`: Plantillas Jinja2 para el frontend
- `static/`: Archivos CSS, JS, iconos y manifest PWA
- `requirements.txt`: Dependencias Python

## Funcionalidades Principales

1. **Gestión de Viajes**: Crear, ver y editar viajes con fechas y presupuesto
2. **Control de Gastos**: Registro por categorías con seguimiento de presupuesto
3. **Actividades**: Planificación de itinerario con fechas y ubicaciones
4. **Documentos**: Gestión de pasaportes, visas, reservas, etc.
5. **PWA**: Instalable como app nativa con modo offline

## Estilo de Código

- Python: PEP 8, funciones claras y comentadas
- HTML: Semántico, accesible, optimizado para móvil
- CSS: Variables CSS, mobile-first, Material Design
- JavaScript: ES6+, funciones modulares, manejo de errores

## Consideraciones Móviles

- Toques táctiles amigables (mínimo 44px)
- Navegación con gestos
- Optimización de rendimiento
- Soporte offline con localStorage
- Instalación PWA

## Próximas Funcionalidades

- Integración con mapas
- Notificaciones push
- Compartir viajes
- Exportar a PDF
- Conversor de monedas
- Modo oscuro

Siempre priorizar la experiencia móvil y mantener el código simple y mantenible.
