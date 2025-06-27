# -*- coding: utf-8 -*-
"""
Modelo para Actividades.
"""

from datetime import date
from . import db


class Actividad(db.Model):
    """Modelo para representar actividades de un viaje."""
    
    id = db.Column(db.Integer, primary_key=True)
    viaje_id = db.Column(db.Integer, db.ForeignKey('viaje.id'), nullable=False)
    destino = db.Column(db.String(100), nullable=False, default='general')  # Destino/lugar de la actividad
    nombre = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time)
    ubicacion = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    completada = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Actividad {self.nombre}: {self.fecha} {"✅" if self.completada else "⏳"}>'
