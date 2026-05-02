from flask import Flask, request, jsonify, send_file
import requests
import datetime
import pickle
import os

app = Flask(__name__)

# ================= CONFIG =================
API_KEY = os.getenv("API_KEY")  # set in Render

# ================= LOAD MODEL =================
model = None
try:
    model_path = os.path.join(os.getcwd(), "model.pkl")
    if os.path.exists(model_path):
        model = pickle.load(open(model_path, "rb"))
        print("✅ Model loaded")
    else:
        print("⚠️ model.pkl not found, using fallback")
except Exception as e:
    print("⚠️ Model load error:", e)

# ================= WEATHER FUNCTION =================
def get_weather(lat, lon):
    try:
        if not API_KEY:
            return 25, 0  # fallback if no API key

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        )

        res = requests.get(url, timeout=5)
        data = res.json()

        temp = data.get("main", {}).get("temp", 25)
        rain = data.get("rain", {}).get("1h", 0)

        return temp, rain

    except Exception as e:
        print("Weather error:", e)
        return 25, 0  # safe fallback

# ================= SERVE FRONTEND =================
@app.route("/")
def home():
    file_path = os.path.join(os.getcwd(), "index.html")
    if os.path.exists(file_path):
        return send_file(file_path)
    return "❌ index.html not found"

# ================= PREDICTION =================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # INPUT VALIDATION
        s_lat = float(data.get("start_lat"))
        s_lon = float(data.get("start_lon"))
        e_lat = float(data.get("end_lat"))
        e_lon = float(data.get("end_lon"))

        # WEATHER DATA
        s_temp, s_rain = get_weather(s_lat, s_lon)
        e_temp, e_rain = get_weather(e_lat, e_lon)

        hour = datetime.datetime.now().hour

        # ML PREDICTION OR FALLBACK
        if model:
            features = [[s_temp, s_rain, e_temp, e_rain, hour]]
            prediction = str(model.predict(features)[0])
        else:
            # Smart fallback logic
            if s_rain > 5 or e_rain > 5 or hour >= 18:
                prediction = "🔴 High Risk Area"
            elif s_temp > 30 or e_temp > 30:
                prediction = "🟡 Medium Risk Area"
            else:
                prediction = "🟢 Low Risk Area"

        return jsonify({
            "prediction": prediction,
            "start_weather": {
                "temp": round(s_temp, 2),
                "rain": round(s_rain, 2)
            },
            "end_weather": {
                "temp": round(e_temp, 2),
                "rain": round(e_rain, 2)
            },
            "hour": hour
        })

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": "Server failed"}), 500


# ================= HEALTH CHECK =================
@app.route("/health")
def health():
    return {"status": "ok"}


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
