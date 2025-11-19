#!/bin/bash

# Simple - Login and run emulationstation

echo "🎮 Opening TTY4 and logging in..."

# Kill any existing TTY4 processes first
sudo fuser -k /dev/tty4 2>/dev/null || true
sleep 1

# Use expect to handle the login and command
expect << 'EOF'
# Switch to TTY4
spawn sudo chvt 4
expect eof
sleep 2

# Open a login session on TTY4
spawn sudo openvt -f -c 4 -s -- /bin/login

# Handle login sequence
expect "login:"
send "kirby\r"

expect "Password:"
send "ese123\r"

expect "kirby@"
send "emulationstation\r"

# Wait for emulationstation to potentially exit
expect eof
EOF

echo "✅ EmulationStation launched"