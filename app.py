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
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Model load error:", e)
    model = None

# Load API key from environment
API_KEY = os.environ.get("API_KEY")
print("API KEY:", API_KEY)  # debug

# Safe weather function (won’t crash)
def get_weather(lat, lon):
    try:
        if not API_KEY:
            print("⚠️ API KEY missing")
            return 25, 0

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=5).json()

        temp = res.get('main', {}).get('temp', 25)
        rain = 1 if 'rain' in res else 0

        return temp, rain

    except Exception as e:
        print("Weather API error:", e)
        return 25, 0  # fallback

# Home route (IMPORTANT)
@app.route('/')
def home():
    return render_template("index.html")

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        lat = float(request.form['lat'])
        lon = float(request.form['lon'])

        temp, rain = get_weather(lat, lon)
        hour = datetime.now().hour

        # Match your training features
        data = np.array([[lat, lon, temp, hour]])

        if model:
            prediction = model.predict(data)[0]
        else:
            prediction = 0  # fallback

        result = "⚠️ High Risk Area" if prediction else "✅ Safe Area"

        return render_template("index.html",
                               prediction_text=result,
                               temp=temp,
                               rain=rain,
                               hour=hour)

    except Exception as e:
        print("Prediction error:", e)
        return render_template("index.html",
                               prediction_text="❌ Error occurred",
                               temp="N/A",
                               rain="N/A",
                               hour="N/A")

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
