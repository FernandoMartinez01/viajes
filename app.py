import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)

# Configuración dinámica para desarrollo y producción
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu-clave-secreta-aqui')

# Base de datos: PostgreSQL en producción, SQLite en desarrollo
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Producción (PostgreSQL) - Corregir URL si es necesario
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Desarrollo (SQLite) - Usar instancia local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/viaje.db'
    print("🗄️  Usando SQLite en desarrollo")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

# Modelos de base de datos
class Viaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)  # Nombre general del viaje
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    presupuesto_total = db.Column(db.Float, default=0.0)
    presupuesto_gastado = db.Column(db.Float, default=0.0)
    notas = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    paradas = db.relationship('Parada', backref='viaje', lazy=True, cascade='all, delete-orphan', order_by='Parada.orden')
    gastos = db.relationship('Gasto', backref='viaje', lazy=True, cascade='all, delete-orphan')
    actividades = db.relationship('Actividad', backref='viaje', lazy=True, cascade='all, delete-orphan')
    documentos = db.relationship('Documento', backref='viaje', lazy=True, cascade='all, delete-orphan')
    transportes = db.relationship('Transporte', backref='viaje', lazy=True, cascade='all, delete-orphan', order_by='Transporte.fecha_salida')
    alojamientos = db.relationship('Alojamiento', backref='viaje', lazy=True, cascade='all, delete-orphan', order_by='Alojamiento.fecha_entrada')

class Parada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    orden = db.Column(db.Integer, nullable=False)  # Orden de la parada en el viaje
    fecha_llegada = db.Column(db.Date, nullable=False)
    fecha_salida = db.Column(db.Date, nullable=False)
    notas = db.Column(db.Text)
    
    # Constraint para evitar paradas duplicadas en el mismo orden
    __table_args__ = (db.UniqueConstraint('viaje_id', 'orden', name='_viaje_orden_uc'),)

class Gasto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # transporte, comida, hospedaje, etc.
    descripcion = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=date.today)
    moneda = db.Column(db.String(3), default='USD')

class Actividad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    destino = db.Column(db.String(100), nullable=False, default='general')  # Destino/lugar de la actividad
    nombre = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time)
    ubicacion = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    completada = db.Column(db.Boolean, default=False)

class Documento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # pasaporte, visa, reserva, etc.
    nombre = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.String(100))
    fecha_vencimiento = db.Column(db.Date)
    notas = db.Column(db.Text)

class Transporte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='vuelo')  # vuelo, tren, bus, etc.
    origen = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    codigo_reserva = db.Column(db.String(50))
    fecha_salida = db.Column(db.Date, nullable=False)
    hora_salida = db.Column(db.Time)
    fecha_llegada = db.Column(db.Date, nullable=False)
    hora_llegada = db.Column(db.Time)
    aerolinea = db.Column(db.String(100))
    numero_vuelo = db.Column(db.String(20))
    terminal = db.Column(db.String(20))
    puerta = db.Column(db.String(10))
    asiento = db.Column(db.String(10))
    notas = db.Column(db.Text)

class Alojamiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    destino = db.Column(db.String(100), nullable=False)  # Filtrado por paradas del viaje
    nombre = db.Column(db.String(200), nullable=False)
    direccion = db.Column(db.String(300), nullable=False)
    fecha_entrada = db.Column(db.Date, nullable=False)
    horario_checkin = db.Column(db.Time, nullable=False)
    fecha_salida = db.Column(db.Date, nullable=False)
    horario_checkout = db.Column(db.Time, nullable=False)
    incluye_desayuno = db.Column(db.Boolean, default=False)
    numero_confirmacion = db.Column(db.String(100))  # Opcional
    codigo_pin = db.Column(db.String(20))  # Opcional
    numero_checkin = db.Column(db.String(50))  # Opcional

# Rutas principales
@app.route('/')
def index():
    # Asegurar que la DB esté inicializada
    ensure_db_initialized()
    
    # Asegurar que la DB esté inicializada (failsafe)
    try:
        viajes = Viaje.query.order_by(Viaje.fecha_inicio.desc()).all()
    except Exception as e:
        print(f"Error de BD, intentando inicializar: {e}")
        init_db_auto()
        viajes = Viaje.query.order_by(Viaje.fecha_inicio.desc()).all()
    
    return render_template('index.html', viajes=viajes, hoy=date.today())

@app.route('/viaje/<int:viaje_id>')
def ver_viaje(viaje_id):
    viaje = Viaje.query.get_or_404(viaje_id)
    
    # Agrupar y ordenar actividades por destino y fecha/hora
    actividades_agrupadas = {}
    for actividad in viaje.actividades:
        destino = actividad.destino or 'general'
        if destino not in actividades_agrupadas:
            actividades_agrupadas[destino] = []
        actividades_agrupadas[destino].append(actividad)
    
    # Ordenar actividades dentro de cada destino por fecha y hora
    for destino in actividades_agrupadas:
        actividades_agrupadas[destino].sort(key=lambda a: (
            a.fecha,
            a.hora if a.hora else datetime.min.time()
        ))
    
    # Crear diccionario ordenado: 'general' primero, luego resto alfabéticamente
    from collections import OrderedDict
    actividades_ordenadas = OrderedDict()
    
    # Primero 'general' si existe
    if 'general' in actividades_agrupadas:
        actividades_ordenadas['general'] = actividades_agrupadas['general']
    
    # Luego el resto ordenado alfabéticamente
    for destino in sorted(actividades_agrupadas.keys()):
        if destino != 'general':
            actividades_ordenadas[destino] = actividades_agrupadas[destino]
    
    return render_template('viaje.html', 
                         viaje=viaje, 
                         actividades_agrupadas=actividades_ordenadas,
                         hoy=date.today())

@app.route('/viaje/<int:viaje_id>/eliminar', methods=['POST'])
def eliminar_viaje(viaje_id):
    try:
        viaje = Viaje.query.get_or_404(viaje_id)
        nombre_viaje = viaje.nombre
        
        print(f"Iniciando eliminación del viaje: {nombre_viaje} (ID: {viaje_id})")
        
        # Contar elementos relacionados antes de eliminar (para logs)
        num_paradas = len(viaje.paradas)
        num_gastos = len(viaje.gastos)
        num_actividades = len(viaje.actividades)
        num_documentos = len(viaje.documentos)
        num_transportes = len(viaje.transportes)
        num_alojamientos = len(viaje.alojamientos)
        
        print(f"Elementos a eliminar:")
        print(f"  - Paradas: {num_paradas}")
        print(f"  - Gastos: {num_gastos}")
        print(f"  - Actividades: {num_actividades}")
        print(f"  - Documentos: {num_documentos}")
        print(f"  - Transportes: {num_transportes}")
        print(f"  - Alojamientos: {num_alojamientos}")
        
        # Verificación adicional: eliminar explícitamente elementos relacionados
        # (aunque el cascade debería manejar esto automáticamente)
        
        # Eliminar paradas
        Parada.query.filter_by(viaje_id=viaje_id).delete()
        print("  ✓ Paradas eliminadas")
        
        # Eliminar gastos
        Gasto.query.filter_by(viaje_id=viaje_id).delete()
        print("  ✓ Gastos eliminados")
        
        # Eliminar actividades
        Actividad.query.filter_by(viaje_id=viaje_id).delete()
        print("  ✓ Actividades eliminadas")
        
        # Eliminar documentos
        Documento.query.filter_by(viaje_id=viaje_id).delete()
        print("  ✓ Documentos eliminados")
        
        # Eliminar transportes
        Transporte.query.filter_by(viaje_id=viaje_id).delete()
        print("  ✓ Transportes eliminados")
        
        # Eliminar alojamientos
        Alojamiento.query.filter_by(viaje_id=viaje_id).delete()
        print("  ✓ Alojamientos eliminados")
        
        # Finalmente, eliminar el viaje
        db.session.delete(viaje)
        print("  ✓ Viaje eliminado")
        
        # Commit de todos los cambios
        db.session.commit()
        print(f"✅ Eliminación completada exitosamente")
        
        total_elementos = num_paradas + num_gastos + num_actividades + num_documentos + num_transportes + num_alojamientos
        
        return jsonify({
            'success': True,
            'message': f'Viaje "{nombre_viaje}" y {total_elementos} elementos relacionados eliminados correctamente'
        })
        
    except Exception as e:
        print(f"❌ Error al eliminar viaje: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al eliminar el viaje: {str(e)}'
        }), 500

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

# Función helper para templates
@app.template_filter('porcentaje_presupuesto')
def porcentaje_presupuesto(gastado, total):
    if total <= 0:
        return 0
    return min(100, (gastado / total) * 100)

# Crear tablas automáticamente en el primer acceso (función legacy)
def init_db():
    return init_db_auto()

# Ruta de health check para Railway
@app.route('/health')
def health_check():
    try:
        # Asegurar que la DB esté inicializada
        ensure_db_initialized()
        
        # Verificar que la app y la DB están funcionando
        viajes_count = Viaje.query.count()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'viajes': viajes_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        print(f"❌ Health check falló: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Endpoint temporal para inicializar DB manualmente
@app.route('/init-db')
def force_init_db():
    try:
        global _db_initialized
        _db_initialized = False  # Forzar re-inicialización
        
        success = init_db_auto()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Base de datos inicializada correctamente',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error al inicializar base de datos',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Manejo global de errores
@app.errorhandler(500)
def internal_error(error):
    print(f"Error 500: {error}")
    import traceback
    traceback.print_exc()
    db.session.rollback()
    return jsonify({
        'error': 'Error interno del servidor',
        'message': 'Ha ocurrido un error inesperado'
    }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'No encontrado',
        'message': 'El recurso solicitado no existe'
    }), 404

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
