# -*- coding: utf-8 -*-
"""
Modelo para Gastos.
"""

from datetime import date
from . import db


class Gasto(db.Model):
    """Modelo para representar gastos de un viaje."""
    
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # transporte, comida, hospedaje, etc.
    descripcion = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=date.today)
    moneda = db.Column(db.String(3), default='USD')

    def __repr__(self):
        return f'<Gasto {self.descripcion}: {self.monto} {self.moneda}>'
