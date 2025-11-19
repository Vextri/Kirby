#!/usr/bin/env python3
"""
Kirby Weather Fetcher - Milestone 1
Simple weather data fetcher that gets current weather and displays condition + temperature
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_weather_openweather(city="London"):
    """
    Fetch weather data from OpenWeatherMap API
    Get free API key at: https://openweathermap.org/api
    """
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not api_key:
        print("❌ Error: No OpenWeatherMap API key found!")
        print("Please set OPENWEATHER_API_KEY in your .env file")
        return None
    
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'  # Celsius
    }
    
    try:
        print(f"🌍 Fetching weather for {city}...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse the important data
        condition = data['weather'][0]['main']
        description = data['weather'][0]['description']
        temperature = round(data['main']['temp'])
        feels_like = round(data['main']['feels_like'])
        humidity = data['main']['humidity']
        
        # Get wind data (convert from m/s to km/h)
        wind_speed = data.get('wind', {}).get('speed', 0) * 3.6  # m/s to km/h
        wind_speed = round(wind_speed, 1)
        
        city_name = data['name']
        country = data['sys']['country']
        
        return {
            'condition': condition,
            'description': description,
            'temperature': temperature,
            'feels_like': feels_like,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'city': city_name,
            'country': country
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching weather data: {e}")
        return None
    except KeyError as e:
        print(f"❌ Error parsing weather data: {e}")
        return None

def get_weather_weatherapi(city="London"):
    """
    Alternative: Fetch weather data from WeatherAPI
    Get free API key at: https://www.weatherapi.com/
    """
    api_key = os.getenv('WEATHERAPI_KEY')
    
    if not api_key:
        print("❌ Error: No WeatherAPI key found!")
        print("Please set WEATHERAPI_KEY in your .env file")
        return None
    
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': api_key,
        'q': city,
        'aqi': 'no'
    }
    
    try:
        print(f"🌍 Fetching weather for {city}...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse the important data
        condition = data['current']['condition']['text']
        temperature = round(data['current']['temp_c'])
        feels_like = round(data['current']['feelslike_c'])
        humidity = data['current']['humidity']
        
        # Get wind data (already in km/h)
        wind_speed = round(data['current']['wind_kph'], 1)
        
        city_name = data['location']['name']
        country = data['location']['country']
        
        return {
            'condition': condition,
            'description': condition.lower(),
            'temperature': temperature,
            'feels_like': feels_like,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'city': city_name,
            'country': country
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching weather data: {e}")
        return None
    except KeyError as e:
        print(f"❌ Error parsing weather data: {e}")
        return None

def display_weather(weather_data):
    """Display weather data in a nice format"""
    if not weather_data:
        print("❌ No weather data to display")
        return
    
    print("\n" + "="*50)
    print("🌤️  CURRENT WEATHER")
    print("="*50)
    print(f"📍 Location: {weather_data['city']}, {weather_data['country']}")
    print(f"🌡️  Temperature: {weather_data['temperature']}°C")
    print(f"🤔 Feels like: {weather_data['feels_like']}°C")
    print(f"☁️  Condition: {weather_data['condition']}")
    print(f"📝 Description: {weather_data['description'].title()}")
    print(f"💧 Humidity: {weather_data['humidity']}%")
    print(f"💨 Wind: {weather_data['wind_speed']} km/h")
    print("="*50)
    
    # Simple Kirby mood based on condition
    condition_lower = weather_data['condition'].lower()
    if 'clear' in condition_lower or 'sun' in condition_lower:
        print("😊 Kirby says: Perfect beach weather! ☀️🏖️")
    elif 'rain' in condition_lower:
        print("☔ Kirby says: Time for my umbrella! 🌧️")
    elif 'cloud' in condition_lower:
        print("☁️ Kirby says: Nice and cozy weather! 🤗")
    elif 'snow' in condition_lower:
        print("❄️ Kirby says: Snow day fun! ⛄")
    elif 'storm' in condition_lower or 'thunder' in condition_lower:
        print("⛈️ Kirby says: Exciting weather! 🌩️")
    else:
        print("🌟 Kirby says: Any weather is good weather! 😄")

def main():
    """Main function to run the weather fetcher"""
    print("🌟 Welcome to Kirby Weather Fetcher - Milestone 1! 🌟")
    
    # Get city from user input or use default
    city = input("\n🏙️ Enter city name (or press Enter for London): ").strip()
    if not city:
        city = "London"
    
    # Try OpenWeatherMap first, then WeatherAPI as backup
    print("\n🔄 Trying OpenWeatherMap API...")
    weather_data = get_weather_openweather(city)
    
    if not weather_data:
        print("\n🔄 Trying WeatherAPI as backup...")
        weather_data = get_weather_weatherapi(city)
    
    # Display the results
    display_weather(weather_data)
    
    if weather_data:
        print(f"\n✅ Successfully fetched weather for {weather_data['city']}!")
    else:
        print("\n❌ Could not fetch weather data. Please check your API keys.")

if __name__ == "__main__":
    main()
