from flask import Flask, render_template, request
import pickle
import numpy as np
import requests
from datetime import datetime

app = Flask(__name__)

model = pickle.load(open("model.pkl", "rb"))

API_KEY = "YOUR_OPENWEATHER_API_KEY"

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()

    temp = res['main']['temp']
    rain = 1 if 'rain' in res else 0

    return temp, rain

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    lat = float(request.form['lat'])
    lon = float(request.form['lon'])

    temp, rain = get_weather(lat, lon)
    hour = datetime.now().hour

    data = np.array([[lat, lon, temp, hour]])

    prediction = model.predict(data)[0]

    result = "⚠️ High Risk Area" if prediction else "✅ Safe Area"

    return render_template("index.html",
                           prediction_text=result,
                           temp=temp,
                           rain=rain,
                           hour=hour)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
