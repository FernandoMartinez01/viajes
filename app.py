import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from config.settings import Config
from app.utils.helpers import porcentaje_presupuesto

app = Flask(__name__)

# Configuración usando el módulo separado
app.config['SECRET_KEY'] = Config.get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.get_sqlalchemy_track_modifications()

db = SQLAlchemy(app)

# Inicializar modelos y obtener las clases
from app.models import init_models
models = init_models(db)

# Asignar modelos a variables globales para fácil acceso
Viaje = models['Viaje']
Parada = models['Parada']
Gasto = models['Gasto']
Actividad = models['Actividad']
Documento = models['Documento']
Transporte = models['Transporte']
Alojamiento = models['Alojamiento']

# Registrar blueprints
from app.routes import register_blueprints
register_blueprints(app)

# Inicializar rutas principales con modelos y funciones necesarias
from app.routes.main import init_main_routes

# Función para inicializar blueprints con dependencias
def init_blueprints_dependencies():
    """Inicializa los blueprints con sus dependencias necesarias."""
    # Funciones helper para manejar _db_initialized de forma segura
    def get_db_initialized_status():
        return globals().get('_db_initialized', False)
    
    def set_db_initialized_status(status):
        globals()['_db_initialized'] = status
    
    # Preparar funciones para las rutas principales
    db_functions = {
        'ensure_db_initialized': ensure_db_initialized,
        'init_db_auto': init_db_auto,
        'get_db_initialized_status': get_db_initialized_status,
        'set_db_initialized_status': set_db_initialized_status
    }
    
    # Inicializar rutas principales
    init_main_routes(models, db_functions)
    
    # Inicializar rutas de viajes
    from app.routes.viajes import init_viajes_routes
    init_viajes_routes(models, db)

# Variable global para controlar la inicialización
_db_initialized = False

# Inicializar base de datos automáticamente
def init_db_auto():
    """Función para inicializar DB que se ejecuta solo cuando es necesario"""
    global _db_initialized
    
    if _db_initialized:
        return True
        
    try:
        print("🔄 Inicializando base de datos...")
        
        # Crear el directorio si no existe (solo para SQLite local)
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"📁 Directorio de DB creado: {db_dir}")
        
        db.create_all()
        print("✅ Tablas de base de datos verificadas/creadas correctamente")
        
        # Verificar que la conexión funciona
        viajes_count = Viaje.query.count()
        print(f"📊 Base de datos conectada correctamente. Viajes existentes: {viajes_count}")
        
        _db_initialized = True
        return True
        
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        import traceback
        traceback.print_exc()
        return False

def ensure_db_initialized():
    """Garantiza que la DB esté inicializada antes de cualquier operación"""
    if not _db_initialized:
        init_db_auto()

# Headers de respuesta para desarrollo
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Expires', '0')
    return response

# Modelos de base de datos importados desde app.models

# Inicializar blueprints con sus dependencias
init_blueprints_dependencies()

# Rutas principales movidas a app/routes/main.py

# Rutas de viajes movidas a app/routes/viajes.py

# Rutas de eliminación de viajes movidas a app/routes/viajes.py

@app.route('/nuevo-viaje', methods=['GET', 'POST'])
def nuevo_viaje():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Crear el viaje principal
        viaje = Viaje(
            nombre=data['nombre'],
            fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date(),
            fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date(),
            presupuesto_total=float(data.get('presupuesto_total', 0)),
            notas=data.get('notas', '')
        )
        
        db.session.add(viaje)
        db.session.flush()  # Para obtener el ID del viaje
        
        # Procesar paradas
        paradas_data = data.get('paradas', [])
        if isinstance(paradas_data, str):
            import json
            paradas_data = json.loads(paradas_data)
        
        for i, parada_data in enumerate(paradas_data):
            parada = Parada(
                viaje_id=viaje.id,
                destino=parada_data['destino'],
                orden=i + 1,
                fecha_llegada=datetime.strptime(parada_data['fecha_llegada'], '%Y-%m-%d').date(),
                fecha_salida=datetime.strptime(parada_data['fecha_salida'], '%Y-%m-%d').date(),
                notas=parada_data.get('notas', '')
            )
            db.session.add(parada)
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'viaje_id': viaje.id})
        return redirect(url_for('ver_viaje', viaje_id=viaje.id))
    
    return render_template('nuevo_viaje.html')

@app.route('/viaje/<int:viaje_id>/gasto', methods=['POST'])
def agregar_gasto(viaje_id):
    data = request.get_json()
    
    gasto = Gasto(
        viaje_id=viaje_id,
        categoria=data['categoria'],
        descripcion=data['descripcion'],
        monto=float(data['monto']),
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        moneda=data.get('moneda', 'USD')
    )
    
    db.session.add(gasto)
    db.session.flush()  # Para que el gasto esté disponible en la relación
    
    # Actualizar presupuesto gastado - solo suma todos los gastos del viaje
    viaje = Viaje.query.get(viaje_id)
    viaje.presupuesto_gastado = sum(g.monto for g in viaje.gastos)
    
    db.session.commit()
    
    return jsonify({'success': True, 'gasto_id': gasto.id})

@app.route('/viaje/<int:viaje_id>/actividad', methods=['POST'])
def agregar_actividad(viaje_id):
    data = request.get_json()
    
    actividad = Actividad(
        viaje_id=viaje_id,
        destino=data.get('destino', 'general'),
        nombre=data['nombre'],
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        hora=datetime.strptime(data['hora'], '%H:%M').time() if data.get('hora') else None,
        ubicacion=data.get('ubicacion', ''),
        descripcion=data.get('descripcion', '')
    )
    
    db.session.add(actividad)
    db.session.commit()
    
    return jsonify({'success': True, 'actividad_id': actividad.id})

@app.route('/viaje/<int:viaje_id>/documento', methods=['POST'])
def agregar_documento(viaje_id):
    data = request.get_json()
    
    documento = Documento(
        viaje_id=viaje_id,
        tipo=data['tipo'],
        nombre=data['nombre'],
        numero=data.get('numero', ''),
        fecha_vencimiento=datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date() if data.get('fecha_vencimiento') else None,
        notas=data.get('notas', '')
    )
    
    db.session.add(documento)
    db.session.commit()
    
    return jsonify({'success': True, 'documento_id': documento.id})

@app.route('/viaje/<int:viaje_id>/transporte', methods=['POST'])
def agregar_transporte(viaje_id):
    data = request.get_json()
    
    transporte = Transporte(
        viaje_id=viaje_id,
        tipo=data.get('tipo', 'vuelo'),
        origen=data['origen'],
        destino=data['destino'],
        codigo_reserva=data.get('codigo_reserva', ''),
        fecha_salida=datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date(),
        hora_salida=datetime.strptime(data['hora_salida'], '%H:%M').time() if data.get('hora_salida') else None,
        fecha_llegada=datetime.strptime(data['fecha_llegada'], '%Y-%m-%d').date(),
        hora_llegada=datetime.strptime(data['hora_llegada'], '%H:%M').time() if data.get('hora_llegada') else None,
        aerolinea=data.get('aerolinea', ''),
        numero_vuelo=data.get('numero_vuelo', ''),
        terminal=data.get('terminal', ''),
        puerta=data.get('puerta', ''),
        asiento=data.get('asiento', ''),
        notas=data.get('notas', '')
    )
    
    db.session.add(transporte)
    db.session.commit()
    
    return jsonify({'success': True, 'transporte_id': transporte.id})

@app.route('/viaje/<int:viaje_id>/alojamiento', methods=['POST'])
def agregar_alojamiento(viaje_id):
    data = request.get_json()
    
    alojamiento = Alojamiento(
        viaje_id=viaje_id,
        destino=data['destino'],
        nombre=data['nombre'],
        direccion=data['direccion'],
        fecha_entrada=datetime.strptime(data['fecha_entrada'], '%Y-%m-%d').date(),
        horario_checkin=datetime.strptime(data['horario_checkin'], '%H:%M').time(),
        fecha_salida=datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date(),
        horario_checkout=datetime.strptime(data['horario_checkout'], '%H:%M').time(),
        incluye_desayuno=data.get('incluye_desayuno', False),
        numero_confirmacion=data.get('numero_confirmacion', ''),
        codigo_pin=data.get('codigo_pin', ''),
        numero_checkin=data.get('numero_checkin', '')
    )
    
    db.session.add(alojamiento)
    db.session.commit()
    
    return jsonify({'success': True, 'alojamiento_id': alojamiento.id})

@app.route('/viaje/<int:viaje_id>/parada', methods=['POST'])
def agregar_parada(viaje_id):
    data = request.get_json()
    
    parada = Parada(
        viaje_id=viaje_id,
        destino=data['destino'],
        orden=999,  # Orden temporal, se reorganizará automáticamente
        fecha_llegada=datetime.strptime(data['fecha_llegada'], '%Y-%m-%d').date(),
        fecha_salida=datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date(),
        notas=data.get('notas', '')
    )
    
    db.session.add(parada)
    db.session.commit()
    
    # Reordenar automáticamente todas las paradas por fecha
    reordenar_paradas_por_fecha(viaje_id)
    
    return jsonify({'success': True, 'parada_id': parada.id})

def reordenar_paradas_por_fecha(viaje_id):
    """
    Reordena automáticamente todas las paradas de un viaje por fecha de llegada.
    En caso de fechas iguales, usa estos criterios de desempate:
    1. Fecha de salida (más temprana primero)
    2. Nombre del destino (alfabéticamente)
    3. ID de la parada (orden de creación)
    """
    try:
        print(f"Reordenando paradas del viaje {viaje_id} por fecha de llegada...")
        
        # Obtener todas las paradas del viaje
        paradas = Parada.query.filter_by(viaje_id=viaje_id).all()
        
        if len(paradas) <= 1:
            print("Solo hay una parada o menos, no se necesita reordenar")
            return
        
        # Ordenar por múltiples criterios
        paradas_ordenadas = sorted(paradas, key=lambda p: (
            p.fecha_llegada,           # 1. Fecha de llegada (principal)
            p.fecha_salida,            # 2. Fecha de salida (desempate)
            p.destino.lower(),         # 3. Destino alfabéticamente
            p.id                       # 4. ID (orden de creación)
        ))
        
        print("Nueva secuencia de paradas:")
        
        # PASO 1: Asignar órdenes temporales únicos (negativos para evitar conflictos)
        print("Paso 1: Asignando órdenes temporales...")
        for i, parada in enumerate(paradas_ordenadas):
            orden_temporal = -(i + 1000)  # Usar números negativos muy grandes
            print(f"  Temp {orden_temporal}: {parada.destino} - Llegada: {parada.fecha_llegada}")
            parada.orden = orden_temporal
        
        # Hacer flush para aplicar cambios temporales
        db.session.flush()
        
        # PASO 2: Asignar los órdenes finales correctos
        print("Paso 2: Asignando órdenes finales...")
        for i, parada in enumerate(paradas_ordenadas):
            nuevo_orden = i + 1
            print(f"  {nuevo_orden}. {parada.destino} - Llegada: {parada.fecha_llegada}")
            parada.orden = nuevo_orden
        
        # Commit final
        db.session.commit()
        print("Reordenamiento automático completado exitosamente")
        
    except Exception as e:
        print(f"Error al reordenar paradas por fecha: {str(e)}")
        db.session.rollback()
        raise

@app.route('/viaje/<int:viaje_id>/reordenar-por-fecha', methods=['POST'])
def reordenar_viaje_por_fecha(viaje_id):
    """Endpoint para reordenar manualmente un viaje por fechas"""
    try:
        reordenar_paradas_por_fecha(viaje_id)
        return jsonify({'success': True, 'message': 'Paradas reordenadas por fecha exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/parada/<int:parada_id>/reordenar', methods=['POST'])
def reordenar_parada(parada_id):
    try:
        data = request.get_json()
        if not data or 'nuevo_orden' not in data:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
            
        nuevo_orden = int(data['nuevo_orden'])
        
        parada = Parada.query.get_or_404(parada_id)
        viaje_id = parada.viaje_id
        orden_actual = parada.orden
        
        print(f"Reordenando parada {parada_id} del orden {orden_actual} al orden {nuevo_orden}")
        
        if orden_actual == nuevo_orden:
            print("El orden no ha cambiado, no se necesita actualizar")
            return jsonify({'success': True})
        
        # Obtener todas las paradas del viaje ordenadas
        paradas = Parada.query.filter_by(viaje_id=viaje_id).order_by(Parada.orden).all()
        
        # Crear una lista temporal con los nuevos órdenes
        paradas_temp = []
        for p in paradas:
            if p.id == parada_id:
                # Esta es la parada que estamos moviendo
                continue
            paradas_temp.append(p)
        
        # Insertar la parada movida en la nueva posición
        # Ajustar posición ya que nuevo_orden es 1-indexed
        nueva_posicion = nuevo_orden - 1
        if nueva_posicion < 0:
            nueva_posicion = 0
        elif nueva_posicion > len(paradas_temp):
            nueva_posicion = len(paradas_temp)
            
        paradas_temp.insert(nueva_posicion, parada)
        
        # Usar valores temporales negativos para evitar conflictos de constraint
        print("Asignando órdenes temporales...")
        for i, p in enumerate(paradas_temp):
            p.orden = -(i + 1)  # Valores negativos temporales
        
        db.session.flush()  # Aplicar cambios temporales
        
        # Ahora asignar los órdenes finales correctos
        print("Asignando órdenes finales...")
        for i, p in enumerate(paradas_temp):
            p.orden = i + 1  # Órdenes finales correctos
        
        db.session.commit()
        
        print(f"Reordenamiento completado exitosamente. Nueva secuencia:")
        for p in paradas_temp:
            print(f"  Parada {p.id} ({p.destino}): orden {p.orden}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error al reordenar parada: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Rutas para editar paradas
@app.route('/parada/<int:parada_id>', methods=['PUT'])
def editar_parada(parada_id):
    try:
        data = request.get_json()
        parada = Parada.query.get_or_404(parada_id)
        viaje_id = parada.viaje_id
        
        # Actualizar campos
        parada.destino = data['destino']
        parada.fecha_llegada = datetime.strptime(data['fecha_llegada'], '%Y-%m-%d').date()
        parada.fecha_salida = datetime.strptime(data['fecha_salida'], '%Y-%m-%d').date()
        parada.notas = data.get('notas', '')
        
        db.session.commit()
        
        # Reordenar automáticamente todas las paradas por fecha
        reordenar_paradas_por_fecha(viaje_id)
        
        return jsonify({
            'success': True,
            'message': 'Parada actualizada y reordenada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar parada: {str(e)}'
        }), 500

@app.route('/parada/<int:parada_id>', methods=['DELETE'])
def eliminar_parada(parada_id):
    try:
        parada = Parada.query.get_or_404(parada_id)
        viaje_id = parada.viaje_id
        orden_eliminada = parada.orden
        
        # Eliminar la parada
        db.session.delete(parada)
        
        # Reordenar las paradas restantes
        Parada.query.filter(
            Parada.viaje_id == viaje_id,
            Parada.orden > orden_eliminada
        ).update({Parada.orden: Parada.orden - 1})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Parada eliminada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al eliminar parada: {str(e)}'
        }), 500

@app.route('/actividad/<int:actividad_id>/completar', methods=['POST'])
def completar_actividad(actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    actividad.completada = not actividad.completada
    db.session.commit()
    
    return jsonify({'success': True, 'completada': actividad.completada})

@app.route('/admin/reordenar-todos-viajes', methods=['POST'])
def reordenar_todos_viajes():
    """Endpoint administrativo para reordenar todas las paradas de todos los viajes por fecha"""
    try:
        viajes = Viaje.query.all()
        reordenados = 0
        
        for viaje in viajes:
            if len(viaje.paradas) > 1:
                print(f"Reordenando viaje: {viaje.nombre} (ID: {viaje.id})")
                reordenar_paradas_por_fecha(viaje.id)
                reordenados += 1
        
        return jsonify({
            'success': True, 
            'message': f'Se reordenaron {reordenados} viajes correctamente'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Registrar función helper como filtro de template
app.template_filter('porcentaje_presupuesto')(porcentaje_presupuesto)

# Crear tablas automáticamente en el primer acceso (función legacy)
def init_db():
    return init_db_auto()

# Rutas de health check y init-db movidas a app/routes/main.py

# Manejadores de errores movidos a app/routes/main.py

if __name__ == '__main__':
    # Inicializar base de datos
    if not init_db():
        print("⚠️  Continuando sin inicialización de DB...")
    
    # Para desarrollo local y producción
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Iniciando servidor en puerto {port}")
    print(f"🔧 Modo debug: {debug_mode}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
