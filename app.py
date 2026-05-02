from flask import Flask, request, jsonify, send_from_directory
import requests
import datetime
import pickle
import os

app = Flask(__name__, static_folder=".")

# ---------- LOAD MODEL ----------
model = None
try:
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    if os.path.exists(model_path):
        model = pickle.load(open(model_path, "rb"))
        print("✅ Model loaded")
    else:
        print("⚠️ model.pkl not found, using fallback logic")
except Exception as e:
    print("⚠️ Model load error:", e)

# ---------- ENV ----------
API_KEY = os.getenv("API_KEY")

# ---------- WEATHER ----------
def get_weather(lat, lon):
    try:
        if not API_KEY:
            raise Exception("API_KEY missing")

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=5)
        data = res.json()

        temp = data.get("main", {}).get("temp", 25)
        rain = data.get("rain", {}).get("1h", 0)

        return temp, rain

    except Exception as e:
        print("Weather error:", e)
        return 25, 0  # fallback

# ---------- FRONTEND ----------
@app.route("/")
def home():
    return send_from_directory(".", "index.html")
    import os
from flask import send_file

@app.route("/")
def home():
    file_path = os.path.join(os.getcwd(), "index.html")

    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "❌ index.html not found in root folder"

# ---------- PREDICT ----------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        s_lat = float(data["start_lat"])
        s_lon = float(data["start_lon"])
        e_lat = float(data["end_lat"])
        e_lon = float(data["end_lon"])

        s_temp, s_rain = get_weather(s_lat, s_lon)
        e_temp, e_rain = get_weather(e_lat, e_lon)

        hour = datetime.datetime.now().hour

        if model:
            features = [[s_temp, s_rain, e_temp, e_rain, hour]]
            prediction = str(model.predict(features)[0])
        else:
            # fallback logic
            if s_rain > 5 or e_rain > 5 or hour >= 18:
                prediction = "🔴 High Risk Area"
            elif s_temp > 30 or e_temp > 30:
                prediction = "🟡 Medium Risk Area"
            else:
                prediction = "🟢 Low Risk Area"

        return jsonify({
            "prediction": prediction,
            "start_weather": {"temp": s_temp, "rain": s_rain},
            "end_weather": {"temp": e_temp, "rain": e_rain},
            "hour": hour
        })

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": str(e)}), 500


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
