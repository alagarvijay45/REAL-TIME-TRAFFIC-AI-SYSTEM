from flask import Flask, request, jsonify, render_template
import requests
import datetime
import pickle
import os

app = Flask(__name__)

# ================= CONFIG =================
API_KEY = os.getenv("API_KEY")

# ================= LOAD MODEL =================
model = None
try:
    if os.path.exists("model.pkl"):
        model = pickle.load(open("model.pkl", "rb"))
        print("✅ Model loaded")
    else:
        print("⚠️ model.pkl not found")
except Exception as e:
    print("Model error:", e)

# ================= WEATHER =================
def get_weather(lat, lon):
    try:
        if not API_KEY:
            return 25, 0

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=5).json()

        temp = res.get("main", {}).get("temp", 25)
        rain = res.get("rain", {}).get("1h", 0)

        return temp, rain

    except:
        return 25, 0

# ================= FRONTEND =================
@app.route("/")
def home():
    return render_template("index.html")  # 🔥 FIXED

# ================= PREDICT =================
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
            # fallback
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
        print("Error:", e)
        return jsonify({"error": "Server error"}), 500


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
