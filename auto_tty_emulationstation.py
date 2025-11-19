#!/usr/bin/env python3
"""
Auto TTY EmulationStation Launcher
Simulates Alt+Ctrl+F4, logs in, and starts EmulationStation
"""

import subprocess
import time
import os
import sys

def log_message(message):
    """Print timestamped log message"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def switch_to_tty4():
    """Switch to TTY4 using chvt command"""
    try:
        log_message("🔄 Switching to TTY4...")
        # Use chvt to switch to virtual terminal 4 (equivalent to Ctrl+Alt+F4)
        result = subprocess.run(['sudo', 'chvt', '4'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            log_message("✅ Successfully switched to TTY4")
            return True
        else:
            log_message(f"❌ Failed to switch to TTY4: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log_message("❌ Timeout while switching to TTY4")
        return False
    except Exception as e:
        log_message(f"❌ Error switching to TTY4: {e}")
        return False

def login_and_launch_emulationstation():
    """Login to TTY4 and launch EmulationStation"""
    try:
        log_message("🔐 Starting automated login process...")
        
        # Create expect script for automated login
        expect_script = '''#!/usr/bin/expect -f
# Auto-login script for TTY4 and EmulationStation launch

set timeout 30

# Start a login session on TTY4
spawn sudo openvt -f -c 4 -s -- /bin/login

# Wait for login prompt
expect {
    "login:" {
        send "kirby\\r"
        exp_continue
    }
    "Password:" {
        send "ese123\\r"
        exp_continue
    }
    -re "kirby@.*:\\$" {
        # Successfully logged in, now launch emulationstation
        send "emulationstation\\r"
        # Keep the session alive
        interact
    }
    timeout {
        puts "Login timeout occurred"
        exit 1
    }
    eof {
        puts "Login session ended unexpectedly"
        exit 1
    }
}
'''
        
        # Write expect script to temporary file
        script_path = '/tmp/auto_login_es.exp'
        with open(script_path, 'w') as f:
            f.write(expect_script)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        log_message("🎮 Launching EmulationStation...")
        
        # Execute the expect script
        process = subprocess.Popen(['expect', script_path], 
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        
        log_message("✅ EmulationStation login process started")
        return True
        
    except Exception as e:
        log_message(f"❌ Error during login process: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    dependencies = ['expect', 'sudo']
    missing = []
    
    for dep in dependencies:
        if subprocess.run(['which', dep], capture_output=True).returncode != 0:
            missing.append(dep)
    
    if missing:
        log_message(f"❌ Missing dependencies: {', '.join(missing)}")
        log_message("Install with: sudo apt-get install expect")
        return False
    
    return True

def kill_existing_processes():
    """Kill any existing TTY4 or EmulationStation processes"""
    try:
        log_message("🔄 Cleaning up existing processes...")
        
        # Kill processes using TTY4
        subprocess.run(['sudo', 'fuser', '-k', '/dev/tty4'], 
                      capture_output=True, stderr=subprocess.DEVNULL)
        
        # Kill any existing emulationstation processes
        subprocess.run(['pkill', '-f', 'emulationstation'], 
                      capture_output=True)
        
        time.sleep(2)
        log_message("✅ Cleanup complete")
        
    except Exception as e:
        log_message(f"⚠️  Warning during cleanup: {e}")

def main():
    """Main execution function"""
    log_message("🚀 Starting Auto TTY EmulationStation Launcher")
    
    # Check if running as root
    if os.geteuid() == 0:
        log_message("❌ This script should not be run as root")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Clean up existing processes
    kill_existing_processes()
    
    # Switch to TTY4 (simulates Alt+Ctrl+F4)
    if not switch_to_tty4():
        log_message("❌ Failed to switch to TTY4")
        sys.exit(1)
    
    # Small delay to ensure TTY switch is complete
    time.sleep(1)
    
    # Login and launch EmulationStation
    if login_and_launch_emulationstation():
        log_message("🎮 EmulationStation should now be running on TTY4")
        log_message("💡 Use Alt+Ctrl+F7 to return to GUI desktop")
    else:
        log_message("❌ Failed to launch EmulationStation")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("⏹️  Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        log_message(f"❌ Unexpected error: {e}")
        sys.exit(1)