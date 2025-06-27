# -*- coding: utf-8 -*-
"""
Modelo para Transportes.
"""

from . import db


class Transporte(db.Model):
    """Modelo para representar transportes de un viaje."""
    
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

    def __repr__(self):
        return f'<Transporte {self.tipo}: {self.origen} → {self.destino} ({self.fecha_salida})>'
