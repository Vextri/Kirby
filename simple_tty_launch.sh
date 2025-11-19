#!/bin/bash

# Simple Auto TTY4 EmulationStation Launcher
# Switches to TTY4 and launches EmulationStation directly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_message() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} ✅ $1"
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')]${NC} ❌ $1"
}

main() {
    log_message "🚀 Launching EmulationStation on TTY4..."
    
    # Clean up any existing processes
    log_message "🔄 Cleaning up..."
    sudo pkill -f emulationstation 2>/dev/null || true
    sudo fuser -k /dev/tty4 2>/dev/null || true
    sleep 1
    
    # Switch to TTY4
    log_message "🔄 Switching to TTY4..."
    sudo chvt 4
    
    # Launch EmulationStation directly on TTY4 as the kirby user
    log_message "🎮 Starting EmulationStation..."
    
    # Method 1: Direct launch on TTY4
    sudo bash -c "
        # Set up environment for TTY4
        export TERM=linux
        export USER=kirby
        export HOME=/home/kirby
        export DISPLAY=
        
        # Change to TTY4 and run EmulationStation as kirby user
        exec sudo -u kirby -H bash -c '
            cd /home/kirby
            exec emulationstation
        ' </dev/tty4 >/dev/tty4 2>&1
    " &
    
    # Give it a moment to start
    sleep 3
    
    # Check if EmulationStation is running
    if pgrep -f emulationstation > /dev/null; then
        log_success "🎮 EmulationStation is now running on TTY4!"
        log_message "💡 Use Alt+Ctrl+F7 to return to GUI desktop"
        log_message "💡 Use Alt+Ctrl+F4 to return to EmulationStation"
    else
        log_error "EmulationStation may not have started properly"
        log_message "🔄 Attempting alternative launch method..."
        
        # Alternative method: Use screen session
        sudo bash -c "
            cd /home/kirby
            sudo -u kirby screen -dmS emulationstation bash -c '
                exec emulationstation </dev/tty4 >/dev/tty4 2>&1
            '
        "
        
        sleep 2
        if pgrep -f emulationstation > /dev/null; then
            log_success "🎮 EmulationStation started via screen session!"
        else
            log_error "Failed to start EmulationStation"
            return 1
        fi
    fi
}

# Handle interrupts gracefully
trap 'echo "Script interrupted"; exit 0' INT TERM

# Run main function
main "$@"