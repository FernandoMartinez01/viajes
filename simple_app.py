"""
Archivo simple para probar que Railway puede ejecutar Python
Sin dependencias complejas, solo Flask básico
"""

from flask import Flask, jsonify
from datetime import datetime
import os

# Crear app básica
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'port': os.environ.get('PORT', 'unknown'),
        'app': 'simple-test'
    })

@app.route('/')
def home():
    return jsonify({
        'message': 'App simple funcionando',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
