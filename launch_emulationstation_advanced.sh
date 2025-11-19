#!/bin/bash

# EmulationStation Launcher Script (Advanced)
# This script properly switches to console mode and runs EmulationStation

echo "🎮 EmulationStation Launcher"
echo "=============================================="

# Check if emulationstation is installed
if ! command -v emulationstation &> /dev/null; then
    echo "❌ EmulationStation not found!"
    echo "💡 Install with: sudo apt install emulationstation"
    exit 1
fi

echo "📺 Preparing to launch EmulationStation..."
echo "⚠️  This will switch to console mode"
echo "⚠️  Press Ctrl+C to cancel, or wait 3 seconds..."

# Countdown
for i in 3 2 1; do
    echo "🕐 Starting in $i..."
    sleep 1
done

echo "🚀 Launching EmulationStation..."

# Method 1: Try direct console launch
echo "📺 Switching to console mode..."

# Kill any running X sessions to free up the console
# sudo systemctl stop lightdm 2>/dev/null || true
# sudo systemctl stop gdm 2>/dev/null || true

# Switch to tty1 and run EmulationStation
sudo bash -c "
    # Switch to tty1
    chvt 1
    
    # Run EmulationStation on tty1 as the original user
    su - $USER -c 'emulationstation'
    
    # After EmulationStation exits, return to graphical mode
    chvt 7 2>/dev/null || chvt 2
"

echo "🎮 EmulationStation session ended"
echo "📺 Returned to desktop mode"