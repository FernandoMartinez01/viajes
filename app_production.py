import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)

# Configuración para producción
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu-clave-secreta-aqui')

# Base de datos: PostgreSQL en producción, SQLite en desarrollo
if os.environ.get('DATABASE_URL'):
    # Producción (PostgreSQL)
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Desarrollo (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///viaje.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ...existing code... (modelos y rutas siguen igual)
