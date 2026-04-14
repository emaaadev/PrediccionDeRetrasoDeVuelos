from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime 

app = Flask(__name__)

URL = "https://endpoint-vuelos-sdk.westus2.inference.ml.azure.com/score"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer TU_LLAVE_AQUI"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        fecha_dt = datetime.strptime(data['fecha'], '%Y-%m-%d')
        hora_limpia = int(data['hora'].replace(':', ''))

        payload = {
            "input_data": {
                "columns": [
                    "MONTH", "DAY_OF_MONTH", "DAY_OF_WEEK", 
                    "OP_UNIQUE_CARRIER", "ORIGIN", "DEST", 
                    "DEP_TIME", "DISTANCE"
                ],
                "index": [0],
                "data": [[
                    fecha_dt.month, 
                    fecha_dt.day, 
                    fecha_dt.isoweekday(), 
                    data['aerolinea'], 
                    data['origen'],    
                    data['destino'],   
                    hora_limpia, 
                    float(data['distancia'])
                ]]
            }
        }

        response = requests.post(URL, json=payload, headers=HEADERS)
        
        if response.status_code != 200:
            return jsonify({"error": "Azure Error", "details": response.text}), response.status_code

        return jsonify(response.json())

    except Exception as e:
        print(f"Error interno: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)