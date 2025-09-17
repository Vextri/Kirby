#!/usr/bin/env python3
"""
Kirby Messaging Web Server - Milestone 4
Flask web interface for sending messages to Kirby
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Message storage file
MESSAGES_FILE = "messages.json"

def get_weather_data(city="Lethbridge, Alberta"):
    """Fetch weather data using WeatherAPI"""
    api_key = os.getenv('WEATHERAPI_KEY')
    
    if not api_key:
        return None
    
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': api_key,
        'q': city,
        'aqi': 'no'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'condition': data['current']['condition']['text'],
            'temperature': round(data['current']['temp_c']),
            'city': data['location']['name'],
            'country': data['location']['country'],
            'region': data['location']['region']
        }
    except Exception as e:
        print(f"❌ Error fetching weather: {e}")
        return None

def save_message(username, message):
    """Save a message to the messages file"""
    try:
        # Load existing messages
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r') as f:
                messages = json.load(f)
        else:
            messages = []
        
        # Add new message
        new_message = {
            'id': str(uuid.uuid4())[:8],  # Short unique ID
            'username': username,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'unix_time': int(time.time())
        }
        
        messages.append(new_message)
        
        # Keep only last 10 messages
        messages = messages[-10:]
        
        # Save back to file
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=2)
        
        print(f"💬 New message from {username}: {message}")
        return True
    except Exception as e:
        print(f"❌ Error saving message: {e}")
        return False

def get_latest_message():
    """Get the most recent message"""
    try:
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r') as f:
                messages = json.load(f)
            if messages:
                return messages[-1]
    except Exception as e:
        print(f"❌ Error reading messages: {e}")
    return None

def get_all_messages():
    """Get all messages (for web display)"""
    try:
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r') as f:
                messages = json.load(f)
            return messages
    except Exception as e:
        print(f"❌ Error reading messages: {e}")
    return []

@app.route('/')
def index():
    """Main Kirby messaging page"""
    weather_data = get_weather_data()
    messages = get_all_messages()
    
    return render_template('index.html', 
                         weather=weather_data, 
                         messages=messages)

@app.route('/send', methods=['POST'])
def send_message():
    """Handle message submission"""
    username = request.form.get('username', '').strip()
    message = request.form.get('message', '').strip()
    
    if not username:
        username = "Anonymous"
    
    if message:
        success = save_message(username, message)
        if success:
            return redirect(url_for('index', sent='true'))
    
    return redirect(url_for('index', error='true'))

@app.route('/api/latest')
def api_latest():
    """API endpoint for the pygame display to get latest message"""
    message = get_latest_message()
    weather = get_weather_data()
    
    return jsonify({
        'message': message,
        'weather': weather,
        'timestamp': int(time.time())
    })

@app.route('/api/messages')
def api_messages():
    """API endpoint to get all messages"""
    messages = get_all_messages()
    return jsonify({'messages': messages})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Kirby Messaging Server',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🌟 Starting Kirby Messaging Server!")
    print(f"📱 Access on local network at: http://{os.popen('hostname -I').read().strip().split()[0]}:5000")
    print("💬 Friends can send messages to Kirby!")
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run server accessible on network
    app.run(host='0.0.0.0', port=5000, debug=False)
