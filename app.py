from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Fetch weather data
def fetch_weather(location):
    # Replace with a real geocoding API for dynamic location handling
    locations = {"Seattle": (47.6097, -122.3331), "New York": (40.7128, -74.0060)}
    latitude, longitude = locations.get(location, (47.6097, -122.3331))

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {"latitude": latitude, "longitude": longitude, "weather": data}
    else:
        return None

# Fetch attractions
def fetch_attractions(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node(around:5000,{lat},{lon})["tourism"];
    out body;
    """
    response = requests.post(overpass_url, data={"data": query})
    if response.status_code == 200:
        data = response.json()
        attractions = [
            element["tags"].get("name", "Unknown Attraction")
            for element in data.get("elements", [])
            if "tags" in element and "name" in element["tags"]
        ]
        return attractions[:10]
    return []

# Suggest packing items
def packing_assistant(weather_data):
    recommendations = []
    daily_weather = weather_data['daily']
    max_temp = daily_weather['temperature_2m_max']
    min_temp = daily_weather['temperature_2m_min']

    if max(max_temp) > 25:
        recommendations.append("Light clothing")
    if min(min_temp) < 10:
        recommendations.append("Warm jacket")
    if "rain" in daily_weather.get("weathercode", []):
        recommendations.append("Umbrella or raincoat")
    return recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    location = request.form.get('location')
    weather_data = fetch_weather(location)
    if weather_data:
        lat, lon = weather_data["latitude"], weather_data["longitude"]
        attractions = fetch_attractions(lat, lon)
        packing_list = packing_assistant(weather_data["weather"])
        return jsonify({
            "weather": weather_data["weather"],
            "attractions": attractions,
            "packing_list": packing_list
        })
    return jsonify({"error": "Unable to fetch data."})

if __name__ == '__main__':
    app.run(debug=True)

