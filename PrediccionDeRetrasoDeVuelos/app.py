from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime 
import os
import json

app = Flask(__name__)

URL = "https://endpoint-vuelos-sdk.westus2.inference.ml.azure.com/score"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('AZURE_API_KEY')}"
        }

        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        fecha_dt = datetime.strptime(data['fecha'], '%Y-%m-%d')
        hora_limpia = int(data['hora'].replace(':', ''))

        payload = {
            "aerolinea": data['aerolinea'],
            "origen": data['origen'],
            "destino": data['destino'],
            "hora_salida": hora_limpia,
            "distancia": float(data['distancia']),
            "tiempo_vuelo_estimado": 45.0,
            "cascading_delay": data.get('cascading_delay', 0),
            "mes": fecha_dt.month,
            "dia_semana": fecha_dt.isoweekday(),
            "festivo": 0
        }

        response = requests.post(URL, json=payload, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": "Azure Error", "details": response.text}), response.status_code

        resultado = json.loads(response.text)
        return jsonify(resultado)

    except Exception as e:
        print(f"Error interno: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)