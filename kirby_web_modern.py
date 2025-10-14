"""
Kirby Weather - Modern Web Interface
A beautiful React-like web interface using Flask and modern CSS
"""

from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Your existing weather and season logic
def get_season_from_temperature(temperature):
    if temperature >= 20:
        return 'summer'
    elif temperature >= 10:
        return 'spring'
    elif temperature >= 0:
        return 'fall'
    else:
        return 'winter'

def get_weather_data():
    """Get current weather data"""
    try:
        # Your existing weather API logic here
        return {
            'temperature': 24,
            'condition': 'Sunny',
            'feels_like': 26,
            'humidity': 45,
            'wind_speed': 12,
            'season': get_season_from_temperature(24)
        }
    except:
        return {
            'temperature': 20,
            'condition': 'Unknown',
            'feels_like': 20,
            'humidity': 50,
            'wind_speed': 0,
            'season': 'spring'
        }

def get_messages():
    """Get community messages"""
    try:
        with open('messages.json', 'r') as f:
            return json.load(f)
    except:
        return [{'message': 'Welcome to Kirby Weather!', 'name': 'System'}]

@app.route('/')
def index():
    return render_template('kirby_modern.html')

@app.route('/api/weather')
def api_weather():
    return jsonify(get_weather_data())

@app.route('/api/messages')
def api_messages():
    return jsonify(get_messages())

if __name__ == '__main__':
    print("🌐 Starting Beautiful Kirby Weather Web Interface!")
    print("🎨 Option 2: Modern Glassmorphism Design")
    print("📱 Responsive and Interactive")
    print("🌟 Open http://localhost:5002 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5002)
