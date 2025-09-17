# 🌟 Kirby Weather Display with Messaging

A delightful weather display featuring Kirby that changes based on temperature and allows friends to send messages remotely!

## 🎯 Features

### ✅ Milestone 1: Weather Fetching
- Real-time weather data from WeatherAPI for Lethbridge, Alberta
- Terminal-based weather information display

### ✅ Milestone 2: Pygame Display  
- Beautiful 800x600 window with Kirby and weather info
- Custom Kirby font support with fallback system
- Clean, readable text with shadows and auto-sizing

### ✅ Milestone 3: Temperature-Based Seasonal Images
- **Summer** (20°C+): Hot weather Kirby images
- **Spring** (10-19°C): Mild weather Kirby images  
- **Fall** (0-9°C): Cool weather Kirby images
- **Winter** (<0°C): Cold weather Kirby images
- Auto-cycling through available images every 30 seconds
- Organized in `images/summer/`, `images/spring/`, `images/fall/`, `images/winter/` folders

### ✅ Milestone 4: Web Messaging Interface
- Flask web server for remote message sending
- Beautiful web interface with Kirby-themed styling
- Messages display on the weather screen with username
- Network accessible for Raspberry Pi deployment
- Auto-refresh and message rotation

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
Create a `.env` file with your WeatherAPI key:
```
WEATHERAPI_KEY=your_api_key_here
```

Get your free API key from: https://weatherapi.com

### 3. Add Kirby Images
Organize your Kirby images in seasonal folders:
```
images/
├── summer/
│   ├── hot_kirby.png
│   └── sunny_kirby.jpg
├── spring/
│   ├── mild_kirby.png
│   └── flower_kirby.jpg
├── fall/
│   ├── cool_kirby.png
│   └── autumn_kirby.jpg
└── winter/
    ├── cold_kirby.png
    └── snow_kirby.jpg
```

### 4. Run the System

**Start the messaging web server:**
```bash
python kirby_web_server.py
```

**Run the weather display (in a new terminal):**
```bash
python kirby_display.py
```

**Send messages via web browser:**
- Local: http://localhost:5000
- Network: http://[your-ip]:5000

## 🎮 Controls

- **ESC** or **Q**: Quit the application
- **R**: Refresh weather data manually
- Messages automatically fetch every 10 seconds
- Images cycle every 30 seconds
- Messages display for 15 seconds each

## 🎨 Customization

### Fonts
The system looks for Kirby fonts in this order:
1. Environment variable: `KIRBY_FONT_PATH`
2. Local files: `fonts/kirby-classic.ttf`, `fonts/kirby.ttf`, etc.
3. System fonts: Comic Sans MS, Arial Rounded, etc.
4. Pygame default font

### Temperature Ranges
Based on Lethbridge, Alberta climate:
- **Summer**: 20°C and above (68°F+)
- **Spring**: 10-19°C (50-66°F)  
- **Fall**: 0-9°C (32-48°F)
- **Winter**: Below 0°C (32°F)

### Message System
- Messages are stored in `messages.json`
- Web interface shows recent messages
- Display rotates through messages every 15 seconds
- Anonymous messages are supported

## 🔧 API Endpoints

- `GET /`: Web interface for sending messages
- `POST /send`: Submit a new message
- `GET /api/latest`: Get the most recent message (JSON)
- `GET /api/messages`: Get all messages (JSON)

## 🌐 Raspberry Pi Deployment

Perfect for running on a Raspberry Pi with a display:

1. Clone to your Pi
2. Install dependencies
3. Set up your API key
4. Add your Kirby images
5. Run both servers
6. Access from any device on your network!

## 📁 Project Structure

```
Kirby/
├── kirby_display.py      # Main pygame weather display
├── kirby_web_server.py   # Flask messaging server
├── weather_fetcher.py    # Terminal weather tool (Milestone 1)
├── templates/
│   └── index.html        # Web messaging interface
├── fonts/
│   └── kirby-classic.ttf # Kirby font file
├── images/
│   ├── summer/           # Hot weather images (20°C+)
│   ├── spring/           # Mild weather images (10-19°C)
│   ├── fall/             # Cool weather images (0-9°C)
│   └── winter/           # Cold weather images (<0°C)
├── messages.json         # Message storage
├── requirements.txt      # Python dependencies
├── .env                  # API keys (create this)
└── README.md            # This file
```

## 🎉 Enjoy!

Your friends can now send messages to Kirby from anywhere on your network, and Kirby will display them along with the current weather. Perfect for a kitchen display, office dashboard, or spreading some joy!

Made with 💖 for Kirby fans and weather enthusiasts!
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
