#!/bin/bash

# Minimal launcher: switch to virtual terminal 2 (TTY2) and exit
# This is intentionally simple — it only switches the active VT.

set -euo pipefail

echo "Killing processes on TTY2, then switching to it..."

# Kill any processes attached to TTY2 to ensure clean switch
sudo pkill -KILL -t tty2 2>/dev/null || true

sleep 1 

sudo chvt 2


exit 0
