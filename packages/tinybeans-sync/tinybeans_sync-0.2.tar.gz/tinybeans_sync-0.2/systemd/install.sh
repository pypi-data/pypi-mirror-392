#!/bin/bash
set -e

if [ "$EUID" -eq 0 ]; then
   echo "Do not run this script as root. It will prompt for sudo when needed."
   exit 1
fi

echo "Installing tinybeans-sync systemd service and timer..."

# Download service and timer templates
curl -o tinybeans-sync.service https://raw.githubusercontent.com/brege/tinybeans-sync/refs/heads/main/systemd/tinybeans-sync.service
curl -o tinybeans-sync.timer https://raw.githubusercontent.com/brege/tinybeans-sync/refs/heads/main/systemd/tinybeans-sync.timer

# Replace user/group placeholders
sed -i "s|/home/__user__|$HOME|g; s/__user__/$USER/g; s/__group__/$(id -gn)/g" tinybeans-sync.service

echo "Moving service and timer files to /etc/systemd/system/..."
sudo mv tinybeans-sync.service /etc/systemd/system/
sudo mv tinybeans-sync.timer /etc/systemd/system/
sudo chown root:root /etc/systemd/system/tinybeans-sync.{service,timer}
sudo chmod 644 /etc/systemd/system/tinybeans-sync.{service,timer}

# Fix SELinux context on Fedora/RHEL
sudo restorecon -v /etc/systemd/system/tinybeans-sync.{service,timer} 2>/dev/null || true

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling and starting tinybeans-sync.timer..."
sudo systemctl enable --now tinybeans-sync.timer

echo ""
echo "Timer installed successfully!"
echo "Status:"
sudo systemctl status tinybeans-sync.timer --no-pager
echo ""
echo "View logs with:"
echo "  sudo journalctl -u tinybeans-sync.service"
echo ""
echo "List timers with:"
echo "  systemctl list-timers"
