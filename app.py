from flask import Flask, request, jsonify
import requests, datetime, pickle

app = Flask(__name__)

model = pickle.load(open("model.pkl", "rb"))

API_KEY = "YOUR_OPENWEATHER_API_KEY"

# 🌦 GET WEATHER FUNCTION
def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()

    temp = res["main"]["temp"]
    rain = res.get("rain", {}).get("1h", 0)

    return temp, rain

# 🚦 PREDICT API
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    s_lat = data["start_lat"]
    s_lon = data["start_lon"]
    e_lat = data["end_lat"]
    e_lon = data["end_lon"]

    # 🌦 BOTH LOCATIONS WEATHER
    s_temp, s_rain = get_weather(s_lat, s_lon)
    e_temp, e_rain = get_weather(e_lat, e_lon)

    hour = datetime.datetime.now().hour

    # 🤖 MODEL INPUT (UPDATED)
    features = [[s_temp, s_rain, e_temp, e_rain, hour]]
    prediction = model.predict(features)[0]

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

if __name__ == "__main__":
    app.run(debug=True)
