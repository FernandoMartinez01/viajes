# Mi Viaje - App de Control de Viajes

Una aplicación web progresiva (PWA) para organizar y controlar todos los aspectos de tus viajes, optimizada para dispositivos móviles.

## 🚀 Características

- **📱 Optimizada para móvil**: Diseño mobile-first con interfaz táctil intuitiva
- **🔄 PWA (Progressive Web App)**: Instalable como app nativa en tu celular
- **💰 Control de presupuesto**: Seguimiento de gastos por categorías
- **📅 Planificación de actividades**: Organiza tu itinerario día a día
- **📋 Gestión de documentos**: Guarda información importante de tu viaje
- **🔄 Modo offline**: Funciona sin conexión y sincroniza cuando vuelves online
- **🎨 Diseño moderno**: Interfaz limpia y atractiva con Material Design

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python Flask
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **PWA**: Service Workers, Web App Manifest
- **Diseño**: Material Design Icons, CSS Grid, Flexbox

## 📦 Instalación

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar o descargar el proyecto**
   ```bash
   # Si usas git
   git clone <url-del-repositorio>
   cd viaje
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

5. **Abrir en el navegador**
   - Ve a `http://localhost:5000`
   - Para instalarlo como PWA en tu móvil, abre la URL en tu navegador móvil y busca la opción "Agregar a pantalla de inicio"

## 📱 Instalación como PWA

### En Android (Chrome):
1. Abre la app en Chrome
2. Toca el menú (3 puntos) → "Agregar a pantalla de inicio"
3. Confirma la instalación

### En iOS (Safari):
1. Abre la app en Safari
2. Toca el botón de compartir
3. Selecciona "Agregar a pantalla de inicio"

## 🏗️ Estructura del Proyecto

```
viaje/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias Python
├── # 🧳 Mi Viaje - Control de Viajes

Una aplicación web progresiva (PWA) para organizar y controlar todos los aspectos de tus viajes. Diseñada para ser instalada como app nativa en dispositivos móviles.

## 🌟 Características

- 📱 **PWA Completa**: Instalable como app nativa en Android/iPhone
- ✈️ **Gestión de Viajes**: Crea, planifica y organiza tus viajes
- 🏨 **Alojamientos**: Gestiona reservas de hoteles con check-in/out
- 🚌 **Transportes**: Organiza vuelos, trenes y otros transportes
- 💰 **Control de Gastos**: Seguimiento de presupuesto por categorías
- 📋 **Actividades**: Planifica tu itinerario por destinos
- 📄 **Documentos**: Gestiona pasaportes, visas y reservas
- 🗺️ **Mapas**: Visualización con Leaflet/OpenStreetMap
- 🌙 **Modo Oscuro**: Interfaz adaptable al sistema
- 📱 **Mobile-First**: Optimizado para dispositivos móviles
- 🔄 **Modo Offline**: Funciona sin conexión a internet

## 🚀 Instalación como App Móvil

### En Android (Chrome/Edge):
1. Abre la aplicación en tu navegador
2. Toca el menú (⋮) → "Instalar aplicación" o "Agregar a pantalla de inicio"
3. Confirma la instalación
4. La app aparecerá en tu lista de aplicaciones

### En iPhone/iPad (Safari):
1. Abre la aplicación en Safari
2. Toca el botón de compartir (□↗)
3. Selecciona "Agregar a pantalla de inicio"
4. Personaliza el nombre si deseas
5. Toca "Agregar"

### En Escritorio:
1. En Chrome/Edge: aparecerá un ícono de instalación en la barra de direcciones
2. Haz clic en él y confirma la instalación
3. La app se abrirá en su propia ventana

## 🌐 Acceso en Vivo

**URL de la aplicación:** [https://viajes-production-5454.up.railway.app](https://viajes-production-5454.up.railway.app)

> Nota: Al ser una app sin autenticación, todos los usuarios comparten los mismos datos. Úsala responsablemente en grupo.

## 💻 Desarrollo Local

### Requisitos
- Python 3.8+
- pip

### Instalación
```bash
# Clonar el repositorio
git clone https://github.com/FernandoMartinez01/viajes.git
cd viajes

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# o source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

### Regenerar Iconos PWA
```bash
# Iconos básicos (solo requiere Pillow)
python generate_icons_simple.py

# Iconos avanzados (requiere cairocffi - complejo en Windows)
python generate_icons.py
```

## 🛠️ Tecnologías

- **Backend**: Python Flask 3.0+ con SQLAlchemy
- **Frontend**: HTML5, CSS3 (Mobile-First), JavaScript vanilla
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **PWA**: Service Worker, Web App Manifest
- **Mapas**: Leaflet.js con OpenStreetMap
- **Iconos**: Material Icons
- **Hosting**: Railway / Render

## 📱 Funcionalidades

### Gestión de Viajes
- Crear viajes con fechas y presupuesto
- Múltiples paradas/destinos con reordenamiento automático
- Vista de cronología y planificación

### Control de Gastos
- Registro por categorías (alojamiento, comida, transporte, etc.)
- Seguimiento de presupuesto en tiempo real
- Visualización de gastos por destino

### Actividades e Itinerario
- Planificación de actividades por destino y fecha
- Marcar actividades como completadas
- Organización automática por ubicación

### Documentos
- Gestión de pasaportes, visas y documentos
- Recordatorios de vencimiento
- Organización de reservas y confirmaciones

### Transportes y Alojamientos
- Detalles completos de vuelos con horarios
- Gestión de reservas de hoteles
- Check-in/check-out automático

## 🤝 Contribuir

¿Quieres mejorar la app? 

1. Fork el proyecto
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## 🔧 Estado del Proyecto

- ✅ PWA completamente funcional
- ✅ Instalable en dispositivos móviles
- ✅ Modo offline operativo
- ✅ Interfaz mobile-first
- ✅ Deploy automático en Railway/Render
- 🔄 Integración de mapas en progreso
- 🔄 Notificaciones push (próximamente)
- 🔄 Exportación a PDF (próximamente).md             # Este archivo
├── static/               # Archivos estáticos
│   ├── css/
│   │   └── style.css     # Estilos principales
│   ├── js/
│   │   └── app.js        # JavaScript principal
│   ├── icons/            # Iconos para PWA
│   ├── manifest.json     # Manifiesto PWA
│   └── sw.js            # Service Worker
└── templates/            # Plantillas HTML
    ├── base.html         # Plantilla base
    ├── index.html        # Página principal
    ├── nuevo_viaje.html  # Formulario nuevo viaje
    ├── viaje.html        # Detalles del viaje
    └── modales.html      # Modales para formularios
```

## 💾 Base de Datos

La aplicación usa SQLite para desarrollo, que se crea automáticamente como `viaje.db`. Las tablas incluyen:

- **Viaje**: Información principal del viaje
- **Gasto**: Registro de gastos por categorías
- **Actividad**: Actividades planificadas
- **Documento**: Documentos importantes del viaje

## 🌐 Deploy a Producción

### Opciones recomendadas (gratis para empezar):

1. **Heroku** (Fácil deployment)
   ```bash
   # Crear Procfile
   echo "web: gunicorn app:app" > Procfile
   
   # Desplegar en Heroku
   heroku create tu-app-viajes
   git push heroku main
   ```

2. **Railway** (Moderno y simple)
   - Conecta tu repositorio Git
   - Railway detecta automáticamente Flask
   - Deploy automático en cada push

3. **Render** (Generoso plan gratuito)
   - Conecta repositorio
   - Configura como Web Service
   - Usar PostgreSQL para producción

4. **PythonAnywhere** (Especializado en Python)
   - Upload de archivos manual
   - Configurar WSGI
   - Dominio gratuito incluido

### Variables de entorno para producción:
```bash
FLASK_ENV=production
DATABASE_URL=postgresql://... # Para PostgreSQL
SECRET_KEY=tu-clave-secreta-muy-segura
```

## 🎯 Funcionalidades Principales

### ✈️ Gestión de Viajes
- Crear viajes con destino, fechas y presupuesto
- Ver estado del viaje (próximo, en curso, completado)
- Notas y detalles adicionales

### 💰 Control de Gastos
- Registrar gastos por categorías (transporte, comida, hospedaje, etc.)
- Seguimiento en tiempo real del presupuesto
- Gráfico visual del progreso de gastos

### 📅 Planificación de Actividades
- Programar actividades con fecha y hora
- Marcar actividades como completadas
- Agregar ubicación y descripción

### 📋 Documentos
- Guardar información de pasaportes, visas, reservas
- Fechas de vencimiento y números de referencia
- Notas adicionales por documento

## 🔧 Personalización

### Agregar nuevas categorías de gastos:
Edita el archivo `templates/modales.html` y agrega opciones al select:
```html
<option value="nueva-categoria">Nueva Categoría</option>
```

### Cambiar colores del tema:
Modifica las variables CSS en `static/css/style.css`:
```css
:root {
    --primary-color: #tu-color;
    --secondary-color: #tu-color;
}
```

### Agregar nuevos tipos de documentos:
Similar a las categorías, edita el modal de documentos.

## 🚀 Futuras Mejoras

- [ ] Integración con mapas para ubicaciones
- [ ] Exportar viaje a PDF
- [ ] Compartir viajes con otros usuarios
- [ ] Notificaciones push para recordatorios
- [ ] Integración con APIs de clima
- [ ] Conversor de monedas en tiempo real
- [ ] Backup automático en la nube
- [ ] Modo oscuro automático
- [ ] Reconocimiento de voz para gastos rápidos

## 🐛 Resolución de Problemas

### La app no se instala como PWA:
- Verifica que estés usando HTTPS (en producción)
- Asegúrate de que los iconos estén disponibles
- Revisa la consola del navegador para errores

### Problemas de base de datos:
```bash
# Eliminar base de datos y reiniciar
rm viaje.db
python app.py
```

### Errores de dependencias:
```bash
# Actualizar pip y reinstalar
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 💡 Consejos de Uso

### Para sacar el máximo provecho:

1. **Planifica antes del viaje**: Crea tu viaje y agrega actividades principales
2. **Registra gastos diariamente**: Mantén tu presupuesto actualizado
3. **Usa categorías consistentes**: Facilita el análisis posterior
4. **Guarda documentos importantes**: Nunca olvides información crucial
5. **Instala como PWA**: Acceso rápido desde tu pantalla de inicio

### Atajos útiles:
- Swipe hacia atrás para navegar
- Pull to refresh en listas
- Toque largo para opciones adicionales (próximamente)

¡Disfruta organizando tus viajes! ✈️🌎
