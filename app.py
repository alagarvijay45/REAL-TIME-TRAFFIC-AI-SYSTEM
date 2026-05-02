from flask import Flask, render_template, request
import pickle
import numpy as np
import requests
from datetime import datetime
import os

app = Flask(__name__)

# Load model safely
try:
    model = pickle.load(open("model.pkl", "rb"))
    print("Model loaded")
except:
    model = None
    print("Model load failed")

# API Key
API_KEY = os.environ.get("API_KEY")

# Safe weather function
def get_weather(lat, lon):
    try:
        if not API_KEY:
            return 25, 0

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=5).json()

        temp = res.get('main', {}).get('temp', 25)
        rain = 1 if 'rain' in res else 0

        return temp, rain
    except:
        return 25, 0

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        lat = float(request.form['lat'])
        lon = float(request.form['lon'])

        temp, rain = get_weather(lat, lon)
        hour = datetime.now().hour

        data = np.array([[lat, lon, temp, hour]])

        prediction = model.predict(data)[0] if model else 0

        # 3-level classification
        if prediction == 1:
            result = "⚠️ High Risk Area"
        elif prediction == 0:
            result = "🟡 Medium Risk Area"
        else:
            result = "✅ Low Risk Area"

        return render_template("index.html",
                               prediction_text=result,
                               temp=temp,
                               rain=rain,
                               hour=hour)

    except Exception as e:
        print("Error:", e)
        return render_template("index.html",
                               prediction_text="Error",
                               temp=0,
                               rain=0,
                               hour=0)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
