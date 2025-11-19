#!/bin/bash

# Auto TTY4 EmulationStation Launcher
# Simulates Alt+Ctrl+F4, logs in, and starts EmulationStation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_message() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ✅ $1"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ❌ $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ⚠️  $1"
}

# Check if expect is installed
check_dependencies() {
    if ! command -v expect &> /dev/null; then
        log_error "expect is not installed"
        log_message "Install with: sudo apt-get install expect"
        exit 1
    fi
}

# Clean up any existing processes
cleanup_processes() {
    log_message "🔄 Cleaning up existing processes..."
    
    # Kill any processes using TTY4
    sudo fuser -k /dev/tty4 2>/dev/null || true
    
    # Kill any existing emulationstation processes
    pkill -f emulationstation 2>/dev/null || true
    
    sleep 2
    log_success "Cleanup complete"
}

# Switch to TTY4 (equivalent to Alt+Ctrl+F4)
switch_to_tty4() {
    log_message "🔄 Switching to TTY4 (Alt+Ctrl+F4 equivalent)..."
    
    if sudo chvt 4; then
        log_success "Successfully switched to TTY4"
        return 0
    else
        log_error "Failed to switch to TTY4"
        return 1
    fi
}

# Auto-login and launch EmulationStation
auto_login_emulationstation() {
    log_message "🔐 Starting automated login and EmulationStation launch..."
    
    # Create temporary expect script
    expect_script=$(mktemp)
    cat > "$expect_script" << 'EOF'
#!/usr/bin/expect -f
set timeout 30

# Method 1: Try direct TTY4 access
spawn sudo su - kirby -c "TERM=linux sudo -u kirby bash -c 'exec emulationstation' </dev/tty4 >/dev/tty4 2>&1" &

sleep 2

# Method 2: If method 1 fails, try login approach
spawn sudo getty 38400 tty4

expect {
    "login:" {
        send "kirby\r"
        exp_continue
    }
    "Password:" {
        send "ese123\r"
        exp_continue
    }
    -re "kirby@.*:\\$|kirby@.*:~\\$" {
        puts "\n🎮 Launching EmulationStation..."
        send "emulationstation\r"
        interact
    }
    timeout {
        puts "\n⚠️ Trying alternative method..."
        # Try direct execution on TTY4
        spawn sudo bash -c "echo 'emulationstation' | sudo -u kirby DISPLAY= TERM=linux /bin/bash - </dev/tty4 >/dev/tty4 2>&1"
        expect eof
    }
    eof {
        puts "\n⚠️ Session ended, trying direct launch..."
        # Try direct execution on TTY4
        spawn sudo bash -c "sudo -u kirby DISPLAY= TERM=linux emulationstation </dev/tty4 >/dev/tty4 2>&1"
        interact
    }
}
EOF

    chmod +x "$expect_script"
    
    # Execute the expect script
    if expect "$expect_script"; then
        log_success "EmulationStation launched successfully"
    else
        log_warning "Expect script completed, trying direct launch method..."
        # Fallback: Direct launch on TTY4
        sudo bash -c "sudo -u kirby DISPLAY= TERM=linux emulationstation </dev/tty4 >/dev/tty4 2>&1 &"
        log_success "EmulationStation launched directly on TTY4"
    fi
    
    # Clean up
    rm -f "$expect_script"
    return 0
}

# Main execution
main() {
    log_message "🚀 Starting Auto TTY EmulationStation Launcher"
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
    
    # Check dependencies
    check_dependencies
    
    # Clean up existing processes
    cleanup_processes
    
    # Switch to TTY4
    if ! switch_to_tty4; then
        exit 1
    fi
    
    # Small delay to ensure TTY switch is complete
    sleep 1
    
    # Auto-login and launch EmulationStation
    if auto_login_emulationstation; then
        log_success "🎮 EmulationStation should now be running on TTY4"
        log_message "💡 Use Alt+Ctrl+F7 to return to GUI desktop"
    else
        log_error "Failed to complete the process"
        exit 1
    fi
}

# Handle interrupts gracefully
trap 'log_warning "Script interrupted by user"; exit 0' INT TERM

# Run main function
main "$@"