# 🚀 Guía de Deployment - Mi Viaje App

## 📊 Base de Datos Actual

Tu base de datos SQLite está en:
```
c:\Users\ferna\OneDrive\Documents\viaje\instance\viaje.db
```

### ¿Qué es SQLite?
- **Archivo único**: No necesita servidor separado
- **Perfecto para desarrollo**: Fácil de usar y configurar
- **Limitaciones**: No ideal para múltiples usuarios simultáneos

---

## 🌐 Opciones de Deployment

### 1. 🟢 **Railway** (RECOMENDADO)

**¿Por qué Railway?**
- ✅ **Gratis** hasta 5$ mensuales
- ✅ **Súper fácil** de configurar
- ✅ **PostgreSQL gratis** incluido
- ✅ **HTTPS automático**
- ✅ **Deployment automático** desde GitHub

**Pasos para deployar:**

1. **Crear cuenta en Railway**
   - Ve a [railway.app](https://railway.app)
   - Regístrate con GitHub

2. **Subir código a GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tu-usuario/mi-viaje-app.git
   git push -u origin main
   ```

3. **Conectar en Railway**
   - "New Project" → "Deploy from GitHub repo"
   - Selecciona tu repositorio
   - Railway detecta automáticamente que es Flask

4. **Agregar base de datos PostgreSQL**
   - En tu proyecto Railway: "New" → "Database" → "Add PostgreSQL"
   - Railway automáticamente crea la variable `DATABASE_URL`

5. **Variables de entorno**
   ```
   SECRET_KEY=tu-clave-super-secreta-aqui
   DATABASE_URL=(automática de Railway)
   ```

6. **¡Listo!** Tu app estará en: `https://tu-app.railway.app`

---

### 2. 🟡 **Render** (Alternativa)

**Ventajas:**
- ✅ Plan gratuito generoso
- ✅ PostgreSQL incluido
- ✅ SSL automático

**Pasos:**
1. Sube código a GitHub
2. Conecta en [render.com](https://render.com)
3. Crea "Web Service" desde GitHub
4. Agrega PostgreSQL database
5. Configura variables de entorno

---

### 3. 🟠 **Heroku** (Clásico)

**Nota:** Ya no es gratis, pero muy confiable

**Pasos:**
1. Instala Heroku CLI
2. ```bash
   heroku create tu-app-viajes
   heroku addons:create heroku-postgresql:mini
   git push heroku main
   ```

---

### 4. 🔵 **PythonAnywhere** (Para principiantes)

**Ventajas:**
- ✅ Plan gratuito disponible
- ✅ Muy fácil para principiantes
- ✅ Consola web incluida

**Pasos:**
1. Crea cuenta en [pythonanywhere.com](https://pythonanywhere.com)
2. Sube archivos vía web
3. Configura WSGI file
4. Listo!

---

## 📱 Convertir a APK (Opcional)

### Usando PWA Builder (Recomendado):

1. **Instala PWA primero**
   - Abre tu app web en Chrome móvil
   - "Agregar a pantalla de inicio"

2. **Generar APK**
   - Ve a [pwabuilder.com](https://pwabuilder.com)
   - Ingresa URL de tu app
   - Descarga APK para Android

### Usando Capacitor (Avanzado):

```bash
npm install -g @capacitor/cli
npx cap init
npx cap add android
npx cap build android
```

---

## 🔧 Preparar para Producción

### 1. Actualizar app.py para producción:

```python
import os

# Configuración dinámica
if os.environ.get('DATABASE_URL'):
    # Producción - PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Desarrollo - SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///viaje.db'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')
```

### 2. Variables de entorno necesarias:

```env
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
DATABASE_URL=postgresql://user:pass@host:port/db
FLASK_ENV=production
```

### 3. Iconos PWA:

Para una PWA completa, necesitas iconos. Usa:
- [PWA Builder Icon Generator](https://www.pwabuilder.com/imageGenerator)
- Sube una imagen 512x512px
- Descarga y reemplaza en `/static/icons/`

---

## 📊 Migración de Datos

### De SQLite a PostgreSQL:

```python
# Script de migración
import sqlite3
import psycopg2
from urllib.parse import urlparse

def migrate_data():
    # Conectar a SQLite
    sqlite_conn = sqlite3.connect('instance/viaje.db')
    
    # Conectar a PostgreSQL
    url = urlparse(os.environ['DATABASE_URL'])
    pg_conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    
    # Migrar datos tabla por tabla
    # ... código de migración
```

---

## 🎯 **Cambios implementados:**

### ✅ **Presupuesto opcional:**
- El campo presupuesto ahora es completamente opcional
- Si no estableces presupuesto, la sección no se muestra
- Puedes agregar gastos sin necesidad de presupuesto
- La interfaz se adapta automáticamente

### 🗺️ **Mapa interactivo:**
- **Mapa hermoso** que muestra todas las paradas del viaje
- **Marcadores numerados** para cada destino
- **Línea conectora** con flechas entre paradas (ruta)
- **Popups informativos** al hacer clic en cada marcador
- **Vista adaptativa** que se ajusta automáticamente a mostrar toda la ruta
- **Geocodificación automática** de nombres de ciudades/países
- **Responsive** y optimizado para móvil

### 🎨 **Características del mapa:**
- Usa OpenStreetMap (gratuito, sin API keys necesarias)
- Marcadores personalizados con números de orden
- Información detallada en cada popup (fechas, notas)
- Línea punteada conectando las paradas en orden
- Se adapta automáticamente al zoom para mostrar toda la ruta
- Compatible con PWA (funciona offline después de cargar)

---

## 🎯 Recomendación Final

**Para empezar AHORA:**

1. ✅ **Railway** - Más fácil y rápido
2. ✅ **GitHub** - Sube tu código
3. ✅ **PostgreSQL** - Escala mejor que SQLite
4. ✅ **PWA** - Ya está lista para instalar

**Tiempo estimado:** 15-30 minutos para tener tu app online!

---

## 🆘 ¿Necesitas ayuda?

Si tienes problemas:
1. Revisa los logs en Railway/Render
2. Verifica variables de entorno
3. Asegúrate que requirements.txt esté actualizado
4. Pregúntame lo que necesites! 😊
