#!/usr/bin/env python3
"""Script to add multiple test messages for scrolling demo"""

import json
import os

# Test messages to add
test_messages = [
    {"message": "Welcome to Kirby Weather! 🌟", "name": "System"},
    {"message": "It's a beautiful day today! The sun is shining bright ☀️", "name": "SunnyBot"},
    {"message": "Kirby looks so adorable in the summer outfit! 💕", "name": "KirbyFan123"},
    {"message": "The temperature is perfect for outdoor activities 🌳", "name": "WeatherWiz"},
    {"message": "Love the new touch interface! Very smooth and intuitive 📱", "name": "UIDesigner"},
    {"message": "The scrolling feature works great! No more missing messages 📜", "name": "TestUser42"},
    {"message": "Pink is definitely Kirby's color! So cute and vibrant 💖", "name": "ColorLover"},
    {"message": "This weather display is now my favorite app! Amazing work 🎉", "name": "AppReviewer"},
    {"message": "The glassmorphism effects look stunning on this interface ✨", "name": "DesignGuru"},
    {"message": "Can't wait to see what weather tomorrow brings! 🌤️", "name": "WeatherFan"},
    {"message": "The gesture controls feel so natural and responsive 👆", "name": "TouchExpert"},
    {"message": "Kirby makes even rainy days look cheerful! 🌧️😊", "name": "OptimistPro"}
]

# Load existing messages or create new file
messages_file = 'messages.json'
if os.path.exists(messages_file):
    with open(messages_file, 'r') as f:
        data = json.load(f)
    existing_messages = data.get('messages', [])
else:
    existing_messages = []

# Add test messages
all_messages = existing_messages + test_messages

# Save to file
with open(messages_file, 'w') as f:
    json.dump({'messages': all_messages}, f, indent=2)

print(f"✅ Added {len(test_messages)} test messages!")
print(f"📊 Total messages now: {len(all_messages)}")
print("🎮 Use 'M' key in the app to view messages and test scrolling!")
