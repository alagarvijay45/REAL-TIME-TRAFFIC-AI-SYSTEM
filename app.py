from flask import Flask, request, jsonify
import requests
import datetime
import pickle
import os

app = Flask(__name__)

# ================= LOAD MODEL =================
model = None
try:
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    model = pickle.load(open(model_path, "rb"))
    print("✅ Model loaded successfully")
except Exception as e:
    print("⚠️ Model not found or failed to load:", e)

# ================= API KEY =================
API_KEY = os.getenv("API_KEY")  # set this in Render

# ================= WEATHER FUNCTION =================
def get_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=5).json()

        temp = res["main"]["temp"]
        rain = res.get("rain", {}).get("1h", 0)

        return temp, rain

    except Exception as e:
        print("Weather fetch failed:", e)
        return 25, 0  # fallback safe values

# ================= HEALTH CHECK =================
@app.route("/")
def home():
    return "🚦 Traffic AI Backend Running"

# ================= PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        s_lat = data["start_lat"]
        s_lon = data["start_lon"]
        e_lat = data["end_lat"]
        e_lon = data["end_lon"]

        # 🌦 Weather for BOTH locations
        s_temp, s_rain = get_weather(s_lat, s_lon)
        e_temp, e_rain = get_weather(e_lat, e_lon)

        hour = datetime.datetime.now().hour

        # 🤖 ML Prediction (if model exists)
        if model:
            features = [[s_temp, s_rain, e_temp, e_rain, hour]]
            prediction = model.predict(features)[0]
        else:
            # fallback logic (so app doesn't crash)
            if s_rain > 5 or e_rain > 5 or hour >= 18:
                prediction = "🔴 High Risk Area"
            elif s_temp > 30 or e_temp > 30:
                prediction = "🟡 Medium Risk Area"
            else:
                prediction = "🟢 Low Risk Area"

        return jsonify({
            "prediction": str(prediction),
            "start_weather": {
                "temp": s_temp,
                "rain": s_rain
            },
            "end_weather": {
                "temp": e_temp,
                "rain": e_rain
            },
            "hour": hour
        })

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": str(e)}), 500


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
