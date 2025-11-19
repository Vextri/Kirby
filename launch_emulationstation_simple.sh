#!/bin/bash

# Simple EmulationStation Launcher
# Uses openvt to run EmulationStation on a virtual terminal

echo "🎮 Simple EmulationStation Launcher"
echo "=================================="

# Check if emulationstation exists
if ! command -v emulationstation &> /dev/null; then
    echo "❌ EmulationStation not found!"
    echo "💡 Install with: sudo apt install emulationstation"
    exit 1
fi

echo "🚀 Launching EmulationStation on virtual terminal..."

# Use openvt to run EmulationStation on tty1
# This is the cleanest method
sudo openvt -c 1 -s -w -- su - $USER -c emulationstation

echo "🎮 EmulationStation session completed"
echo "📺 Back to desktop"