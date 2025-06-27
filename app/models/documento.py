# -*- coding: utf-8 -*-
"""
Modelo para Documentos.
"""

from . import db


class Documento(db.Model):
    """Modelo para representar documentos de un viaje."""
    
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # pasaporte, visa, reserva, etc.
    nombre = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.String(100))
    fecha_vencimiento = db.Column(db.Date)
    notas = db.Column(db.Text)

    def __repr__(self):
        return f'<Documento {self.tipo}: {self.nombre}>'
