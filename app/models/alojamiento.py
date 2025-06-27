# -*- coding: utf-8 -*-
"""
Modelo para Alojamientos.
"""

from . import db


class Alojamiento(db.Model):
    """Modelo para representar alojamientos de un viaje."""
    
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

    def __repr__(self):
        return f'<Alojamiento {self.nombre} en {self.destino}: {self.fecha_entrada} - {self.fecha_salida}>'
