# Kirby Weather Display - Milestone 1

A simple weather fetcher that displays current weather conditions and temperature in the terminal.

## Milestone 1 Goals ✅
- ✅ Use requests library to fetch weather data
- ✅ Get API key from OpenWeatherMap or WeatherAPI  
- ✅ Parse weather condition and temperature
- ✅ Display results in terminal

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a Weather API Key

**Option A: OpenWeatherMap (Recommended)**
1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Get your API key

**Option B: WeatherAPI (Backup)**
1. Go to https://www.weatherapi.com/
2. Sign up for a free account  
3. Get your API key

### 3. Configure Environment
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# OPENWEATHER_API_KEY=your_actual_api_key_here
```

### 4. Run the Weather Fetcher
```bash
python weather_fetcher.py
```

## Features

- 🌍 **City Selection**: Enter any city name or use default (London)
- 🌡️ **Temperature Display**: Shows current temperature and "feels like"
- ☁️ **Weather Conditions**: Current weather condition and description
- 💧 **Additional Data**: Humidity information
- 🎭 **Kirby Reactions**: Simple Kirby responses to different weather
- 🔄 **Dual API Support**: Falls back to WeatherAPI if OpenWeatherMap fails

## Sample Output

```
🌟 Welcome to Kirby Weather Fetcher - Milestone 1! 🌟

🏙️ Enter city name (or press Enter for London): Tokyo

🌍 Fetching weather for Tokyo...

==================================================
🌤️  CURRENT WEATHER
==================================================
📍 Location: Tokyo, Japan
🌡️  Temperature: 23°C
🤔 Feels like: 25°C
☁️  Condition: Clear
📝 Description: Clear Sky
💧 Humidity: 65%
==================================================
😊 Kirby says: Perfect beach weather! ☀️🏖️

✅ Successfully fetched weather for Tokyo!
```

## Next Milestones

- **Milestone 2**: Add image display capabilities
- **Milestone 3**: Create web interface
- **Milestone 4**: Add LCD display support
- **Milestone 5**: Remote connectivity features
