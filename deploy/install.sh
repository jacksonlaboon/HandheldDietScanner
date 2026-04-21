#!/bin/bash
# Installation script for HandheldDietScanner on Raspberry Pi

echo "=== HandheldDietScanner Installation Script ==="

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This script is designed for Raspberry Pi"
fi

# Update system packages
echo "Updating system packages..."
sudo apt-get update

# Install Python dependencies
echo "Installing Python dependencies..."
sudo apt-get install -y python3-pip python3-venv python3-dev

# Install system dependencies for pygame
echo "Installing system dependencies..."
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Create virtual environment (optional but recommended)
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install project dependencies
echo "Installing project dependencies..."
pip install -r requirements.txt

# Install the package
echo "Installing HandheldDietScanner package..."
pip install -e .

# Set up auto-start service
echo "Setting up auto-start service..."
sudo cp deploy/diet-scanner.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable diet-scanner.service

# Create data directory
echo "Creating data directory..."
mkdir -p data/captures

# Set permissions
echo "Setting permissions..."
sudo chown -R $USER:$USER .

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "To run manually:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "To start auto-start service:"
echo "  sudo systemctl start diet-scanner.service"
echo ""
echo "To view logs:"
echo "  journalctl -u diet-scanner.service -f"
echo ""
echo "To disable auto-start:"
echo "  sudo systemctl disable diet-scanner.service"