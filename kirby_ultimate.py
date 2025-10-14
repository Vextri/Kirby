"""
Kirby Weather - Ultimate Modern Interface
Using FastAPI + React-style components with real-time updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio
from datetime import datetime
import uvicorn

app = FastAPI(title="Kirby Weather Station", version="2.0")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def get_home():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌸 Kirby Weather Station Ultimate</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            overflow-x: hidden;
        }

        .app-container {
            display: grid;
            grid-template-columns: 1fr 400px;
            grid-template-rows: auto 1fr;
            gap: 2rem;
            padding: 2rem;
            min-height: 100vh;
        }

        .header {
            grid-column: 1 / -1;
            text-align: center;
            color: white;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientFlow 4s ease infinite;
        }

        @keyframes gradientFlow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        .kirby-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(15px);
            border-radius: 25px;
            padding: 3rem;
            border: 1px solid rgba(255, 255, 255, 0.15);
            position: relative;
            overflow: hidden;
        }

        .kirby-section::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(from 0deg, transparent, rgba(255, 182, 193, 0.1), transparent);
            animation: rotate 10s linear infinite;
        }

        @keyframes rotate {
            to { transform: rotate(360deg); }
        }

        .kirby-container {
            position: relative;
            z-index: 1;
        }

        .kirby-image {
            width: 300px;
            height: 300px;
            border-radius: 50%;
            object-fit: cover;
            filter: drop-shadow(0 0 30px rgba(255, 182, 193, 0.6));
            animation: float 3s ease-in-out infinite, pulse 2s ease-in-out infinite alternate;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }

        @keyframes pulse {
            0% { filter: drop-shadow(0 0 30px rgba(255, 182, 193, 0.6)); }
            100% { filter: drop-shadow(0 0 50px rgba(255, 182, 193, 0.9)); }
        }

        .weather-panel {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .weather-card, .messages-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            transition: all 0.3s ease;
        }

        .weather-card:hover, .messages-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.15);
        }

        .temperature {
            font-size: 4rem;
            font-weight: 300;
            text-align: center;
            margin-bottom: 1rem;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
        }

        .condition {
            text-align: center;
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            opacity: 0.9;
        }

        .weather-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        .weather-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .weather-label {
            font-size: 0.9rem;
            opacity: 0.7;
            margin-bottom: 0.5rem;
        }

        .weather-value {
            font-size: 1.2rem;
            font-weight: 600;
        }

        .message {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid #4ecdc4;
            transition: all 0.3s ease;
        }

        .message:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(10px);
        }

        .message-text {
            margin-bottom: 1rem;
            line-height: 1.6;
        }

        .message-author {
            text-align: right;
            opacity: 0.7;
            font-size: 0.9rem;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .status-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 600;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .status-connected {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
        }

        .status-disconnected {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }

        @media (max-width: 768px) {
            .app-container {
                grid-template-columns: 1fr;
                padding: 1rem;
            }
            
            .title { font-size: 2rem; }
            .kirby-image { width: 200px; height: 200px; }
            .temperature { font-size: 3rem; }
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef } = React;

        function App() {
            const [weather, setWeather] = useState(null);
            const [messages, setMessages] = useState([]);
            const [connected, setConnected] = useState(false);
            const [currentTime, setCurrentTime] = useState(new Date());
            const ws = useRef(null);

            useEffect(() => {
                // Connect to WebSocket
                ws.current = new WebSocket(`ws://${window.location.host}/ws`);
                
                ws.current.onopen = () => {
                    setConnected(true);
                    console.log('Connected to Kirby Weather Station');
                };

                ws.current.onclose = () => {
                    setConnected(false);
                    console.log('Disconnected from Kirby Weather Station');
                };

                ws.current.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'weather') {
                        setWeather(data.data);
                    } else if (data.type === 'messages') {
                        setMessages(data.data);
                    }
                };

                // Update time every second
                const timeInterval = setInterval(() => {
                    setCurrentTime(new Date());
                }, 1000);

                return () => {
                    clearInterval(timeInterval);
                    if (ws.current) {
                        ws.current.close();
                    }
                };
            }, []);

            const KirbySection = () => (
                <div className="kirby-section">
                    <div className="kirby-container">
                        {weather ? (
                            <img 
                                src={`/static/images/${weather.season}/kirby.png`}
                                alt="Kirby"
                                className="kirby-image"
                                onError={(e) => {
                                    e.target.style.display = 'none';
                                    e.target.nextSibling.style.display = 'block';
                                }}
                            />
                        ) : (
                            <div className="loading"></div>
                        )}
                        <div style={{display: 'none', fontSize: '10rem'}}>🌸</div>
                    </div>
                    
                    {weather && (
                        <div style={{textAlign: 'center', marginTop: '2rem', color: 'white'}}>
                            <h2>Season: {weather.season.charAt(0).toUpperCase() + weather.season.slice(1)}</h2>
                            <p style={{opacity: 0.8, marginTop: '1rem'}}>
                                Kirby changes with the seasons based on temperature!
                            </p>
                        </div>
                    )}
                </div>
            );

            const WeatherCard = () => (
                <div className="weather-card">
                    {weather ? (
                        <>
                            <div className="temperature">{weather.temperature}°C</div>
                            <div className="condition">{weather.condition}</div>
                            
                            <div className="weather-grid">
                                <div className="weather-item">
                                    <div className="weather-label">Feels like</div>
                                    <div className="weather-value">{weather.feels_like}°</div>
                                </div>
                                <div className="weather-item">
                                    <div className="weather-label">Humidity</div>
                                    <div className="weather-value">{weather.humidity}%</div>
                                </div>
                                <div className="weather-item">
                                    <div className="weather-label">Wind Speed</div>
                                    <div className="weather-value">{weather.wind_speed} km/h</div>
                                </div>
                                <div className="weather-item">
                                    <div className="weather-label">Updated</div>
                                    <div className="weather-value">{currentTime.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</div>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div style={{textAlign: 'center'}}>
                            <div className="loading"></div>
                            <p style={{marginTop: '1rem'}}>Loading weather...</p>
                        </div>
                    )}
                </div>
            );

            const MessagesCard = () => (
                <div className="messages-card">
                    <h3 style={{marginBottom: '1.5rem', fontSize: '1.5rem'}}>💌 Community Messages</h3>
                    
                    {messages.length > 0 ? (
                        <div style={{maxHeight: '300px', overflowY: 'auto'}}>
                            {messages.slice(0, 5).map((message, index) => (
                                <div key={index} className="message">
                                    <div className="message-text">{message.message}</div>
                                    <div className="message-author">— {message.name}</div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div style={{textAlign: 'center'}}>
                            <div className="loading"></div>
                            <p style={{marginTop: '1rem'}}>Loading messages...</p>
                        </div>
                    )}
                </div>
            );

            return (
                <div className="app-container">
                    <div className={`status-indicator ${connected ? 'status-connected' : 'status-disconnected'}`}>
                        {connected ? '🟢 Live' : '🔴 Offline'}
                    </div>

                    <header className="header">
                        <h1 className="title">✨ Kirby Weather Station Ultimate ✨</h1>
                        <p style={{opacity: 0.8, marginTop: '1rem', fontSize: '1.1rem'}}>
                            Lethbridge, Alberta • Real-time Weather • {currentTime.toLocaleDateString()}
                        </p>
                    </header>

                    <KirbySection />
                    
                    <div className="weather-panel">
                        <WeatherCard />
                        <MessagesCard />
                    </div>
                </div>
            );
        }

        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        # Send initial data
        await websocket.send_json({
            "type": "weather",
            "data": {
                "temperature": 24,
                "condition": "Sunny",
                "feels_like": 26,
                "humidity": 45,
                "wind_speed": 12,
                "season": "summer"
            }
        })
        
        # Load and send messages
        try:
            with open('messages.json', 'r') as f:
                messages = json.load(f)
            await websocket.send_json({
                "type": "messages",
                "data": messages
            })
        except:
            await websocket.send_json({
                "type": "messages", 
                "data": [{"message": "Welcome to Kirby Weather!", "name": "System"}]
            })
        
        # Keep connection alive and send updates
        while True:
            await asyncio.sleep(30)  # Update every 30 seconds
            
            # Send updated weather data
            await websocket.send_json({
                "type": "weather",
                "data": {
                    "temperature": 24,
                    "condition": "Sunny",
                    "feels_like": 26,
                    "humidity": 45,
                    "wind_speed": 12,
                    "season": "summer"
                }
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("🚀 Starting Kirby Weather Station Ultimate!")
    print("🌐 Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
