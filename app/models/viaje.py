# -*- coding: utf-8 -*-
"""
Modelos para Viajes y Paradas.
"""

from datetime import datetime, date
from . import db


class Viaje(db.Model):
    """Modelo para representar un viaje completo."""
    
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

    def __repr__(self):
        return f'<Viaje {self.nombre}: {self.fecha_inicio} - {self.fecha_fin}>'


class Parada(db.Model):
    """Modelo para representar una parada/destino dentro de un viaje."""
    
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    orden = db.Column(db.Integer, nullable=False)  # Orden de la parada en el viaje
    fecha_llegada = db.Column(db.Date, nullable=False)
    fecha_salida = db.Column(db.Date, nullable=False)
    notas = db.Column(db.Text)
    
    # Constraint para evitar paradas duplicadas en el mismo orden
    __table_args__ = (db.UniqueConstraint('viaje_id', 'orden', name='_viaje_orden_uc'),)

    def __repr__(self):
        return f'<Parada {self.orden}: {self.destino} ({self.fecha_llegada} - {self.fecha_salida})>'
