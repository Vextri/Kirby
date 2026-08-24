#!/bin/bash
# Waits for the Kirby web server (and network) to be ready, then launches the display.
# Installed as a desktop autostart entry by deploy/install.sh so it runs on login,
# after kirby-web.service has had a chance to come up.

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"

ready=false
for i in $(seq 1 30); do
    if curl -fsS http://localhost:5000/health >/dev/null 2>&1; then
        ready=true
        break
    fi
    sleep 2
done

if [ "$ready" = false ]; then
    echo "$(date): kirby-web server not reachable after 60s, starting display without it" \
        >> "$APP_DIR/kirby-display-wrapper.log"
fi

exec "$APP_DIR/venv/bin/python" kirby_display.py
