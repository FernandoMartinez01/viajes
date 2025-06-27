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
├── README.md             # Este archivo
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
