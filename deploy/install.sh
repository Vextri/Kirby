#!/bin/bash
# One-time setup for running Kirby on a Raspberry Pi so it comes up on its own
# every time it's powered on:
#   - installs system + Python dependencies
#   - installs Tailscale and connects this device to your tailnet
#   - installs a systemd service for the messaging server (starts on boot)
#   - installs an autostart entry so the display launches on desktop login
#
# Run from inside the cloned repo:
#   chmod +x deploy/install.sh
#   ./deploy/install.sh
#
# To connect to Tailscale non-interactively (e.g. on a fresh SD card with no
# monitor), generate a reusable auth key at https://login.tailscale.com/admin/settings/keys
# and run instead:
#   TAILSCALE_AUTHKEY=tskey-... ./deploy/install.sh

set -e

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_USER="$(whoami)"

echo "==> Installing system packages"
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip curl \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libfreetype6-dev libjpeg-dev

echo "==> Setting up Python virtual environment"
cd "$APP_DIR"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

if [ ! -f "$APP_DIR/.env" ]; then
    echo "==> No .env found — copying .env.example. Add your real WeatherAPI key before starting the services."
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
fi

echo "==> Installing Tailscale"
if ! command -v tailscale >/dev/null 2>&1; then
    curl -fsSL https://tailscale.com/install.sh | sh
fi
sudo systemctl enable --now tailscaled

if [ -n "$TAILSCALE_AUTHKEY" ]; then
    sudo tailscale up --authkey="$TAILSCALE_AUTHKEY" --hostname=kirby --ssh
else
    echo "==> Starting Tailscale — if this device isn't already authenticated, follow the printed URL to log in"
    sudo tailscale up --hostname=kirby --ssh
fi

echo "==> Installing systemd service for the messaging server"
sed -e "s#__APP_DIR__#$APP_DIR#g" -e "s#__USER__#$APP_USER#g" \
    "$APP_DIR/deploy/kirby-web.service" | sudo tee /etc/systemd/system/kirby-web.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now kirby-web.service

echo "==> Installing autostart entry for the display"
mkdir -p "$HOME/.config/autostart"
chmod +x "$APP_DIR/deploy/kirby-display-wrapper.sh"
sed -e "s#__APP_DIR__#$APP_DIR#g" \
    "$APP_DIR/deploy/kirby-display.desktop" > "$HOME/.config/autostart/kirby-display.desktop"

echo "==> Enabling desktop auto-login (so the display starts with no manual login)"
if command -v raspi-config >/dev/null 2>&1; then
    sudo raspi-config nonint do_boot_behaviour B4
else
    echo "    raspi-config not found — enable Desktop Autologin manually via raspi-config > System Options > Boot / Auto Login"
fi

echo ""
echo "==> Done!"
LOCAL_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
[ -n "$LOCAL_IP" ] && echo "Messaging server (LAN):       http://$LOCAL_IP:5000"
TS_IP="$(tailscale ip -4 2>/dev/null || true)"
[ -n "$TS_IP" ] && echo "Messaging server (Tailscale): http://$TS_IP:5000  <- reachable from anywhere on your tailnet"
echo ""
echo "kirby-web.service is enabled and running now (check: sudo systemctl status kirby-web)."
echo "The display will start automatically the next time this user logs into the desktop."
echo "Reboot to test the full auto-start flow: sudo reboot"
