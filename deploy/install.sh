#!/bin/bash
# Installation script for HandheldDietScanner on Raspberry Pi Zero 2W
set -e

echo "=== HandheldDietScanner Installation Script ==="

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This script is designed for Raspberry Pi"
fi

# ---------------------------------------------------------------------------
# Resolve boot partition path (Pi OS Bookworm moved it to /boot/firmware/)
# ---------------------------------------------------------------------------
if [ -f /boot/firmware/config.txt ]; then
    BOOT_CONFIG=/boot/firmware/config.txt
    BOOT_CMDLINE=/boot/firmware/cmdline.txt
else
    BOOT_CONFIG=/boot/config.txt
    BOOT_CMDLINE=/boot/cmdline.txt
fi
echo "Boot partition: $(dirname "$BOOT_CONFIG")"

# ---------------------------------------------------------------------------
# 1. System packages
# ---------------------------------------------------------------------------
echo "Updating system packages..."
sudo apt-get update

echo "Installing Python dependencies..."
sudo apt-get install -y python3-pip python3-venv python3-dev

echo "Installing SDL2 dependencies for pygame..."
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Spec: Open Sans typography (body 18pt, warnings 24pt)
echo "Installing Open Sans font..."
sudo apt-get install -y fonts-open-sans

# Spec: Tesseract 5.0 LSTM + OpenCV for the vision/OCR pipeline
echo "Installing Tesseract 5 and OpenCV..."
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
# System OpenCV avoids a ~30-min source compile on the Pi Zero 2W
sudo apt-get install -y python3-opencv

# Resistive touch support (Waveshare 3.5" uses tslib/evdev)
echo "Installing touch screen support..."
sudo apt-get install -y libts-dev libts-bin evtest

# ---------------------------------------------------------------------------
# Waveshare 3.5" SPI display driver (ili9486 / fbtft)
# Writes dtoverlay + SPI enable to config.txt so /dev/fb1 is created at boot.
# ---------------------------------------------------------------------------
echo "Configuring Waveshare 3.5\" SPI display driver..."

# Verify the overlay .dtbo file ships with this Pi OS image.
OVERLAY_DIR="$(dirname "$BOOT_CONFIG")/overlays"
if [ ! -f "$OVERLAY_DIR/waveshare35a.dtbo" ]; then
    echo ""
    echo "ERROR: $OVERLAY_DIR/waveshare35a.dtbo not found."
    echo "The Waveshare 3.5\" overlay is not bundled with this Pi OS image."
    echo "Install it with Waveshare's driver installer, then re-run this script:"
    echo "  git clone https://github.com/waveshare/LCD-show.git"
    echo "  cd LCD-show && sudo ./LCD35-show"
    echo "(The Waveshare installer reboots the Pi; run install.sh again afterwards.)"
    echo ""
    exit 1
fi

if ! grep -q "dtoverlay=waveshare35a" "$BOOT_CONFIG" 2>/dev/null; then
    echo "Adding Waveshare 3.5\" display overlay to $BOOT_CONFIG..."
    sudo tee -a "$BOOT_CONFIG" > /dev/null <<'DISPLAY_CFG'

# --- Waveshare 3.5" SPI resistive touchscreen (ili9486, fbtft) ---
dtparam=spi=on
dtoverlay=waveshare35a:rotate=90
# Route output exclusively to the SPI framebuffer; disable HDMI
hdmi_force_hotplug=0
DISPLAY_CFG
else
    echo "Waveshare display overlay already present in $BOOT_CONFIG"
fi

# ---------------------------------------------------------------------------
# CSI Camera (OV5647 / Camera Module 1 on the Pi Zero 2W)
# camera_auto_detect=1 is the modern way (Bullseye+); it replaces the old
# start_x=1 / gpu_mem=128 approach and works with picamera2 / libcamera.
# ---------------------------------------------------------------------------
echo "Enabling CSI camera..."
if ! grep -q "camera_auto_detect" "$BOOT_CONFIG" 2>/dev/null; then
    echo "Adding camera_auto_detect=1 to $BOOT_CONFIG..."
    sudo tee -a "$BOOT_CONFIG" > /dev/null <<'CAMERA_CFG'

# --- CSI camera (OV5647, picamera2 / libcamera) ---
camera_auto_detect=1
CAMERA_CFG
else
    echo "camera_auto_detect already present in $BOOT_CONFIG"
fi

# picamera2 is shipped with Pi OS; prefer the system package
sudo apt-get install -y python3-picamera2 || \
    echo "python3-picamera2 not found — install manually if camera capture is needed"

# ---------------------------------------------------------------------------
# Udev rule: create a stable /dev/input/touchscreen symlink for the
# Waveshare resistive panel.  The SDL service unit references this path via
# SDL_MOUSEDEV=/dev/input/touchscreen.
# The ADS7846 is the touch controller used on Waveshare 3.5" panels.
# ---------------------------------------------------------------------------
echo "Installing udev rule for /dev/input/touchscreen..."
UDEV_RULE=/etc/udev/rules.d/95-waveshare-touch.rules
sudo tee "$UDEV_RULE" > /dev/null <<'UDEV_EOF'
# Waveshare 3.5" resistive touchscreen (ADS7846 / SPI)
SUBSYSTEM=="input", KERNEL=="event*", ATTRS{name}=="ADS7846 Touchscreen", SYMLINK+="input/touchscreen"
UDEV_EOF
sudo udevadm control --reload-rules
sudo udevadm trigger

# ---------------------------------------------------------------------------
# TSLIB configuration
# /etc/ts.conf tells tslib which raw input device to read.  The SDL service
# unit sets SDL_MOUSEDRV=TSLIB; without this file SDL falls back to raw mouse
# events and touch coordinates will be wrong.
# ---------------------------------------------------------------------------
echo "Configuring tslib (/etc/ts.conf)..."
sudo tee /etc/ts.conf > /dev/null <<'TSCONF_EOF'
# tslib configuration for Waveshare 3.5" resistive touch (ADS7846)
module_raw input
module pthres pmin=1
module dejitter delta=100
module linear
TSCONF_EOF

# Point tslib at the symlink created by the udev rule above.
# These are written to /etc/environment so they are available system-wide
# (the service unit also sets them explicitly for safety).
if ! grep -q "TSLIB_TSDEVICE" /etc/environment 2>/dev/null; then
    echo 'TSLIB_TSDEVICE=/dev/input/event2'  | sudo tee -a /etc/environment
    echo 'TSLIB_FBDEV=/dev/fb0'              | sudo tee -a /etc/environment
    echo 'TSLIB_CALIBFILE=/etc/pointercal'   | sudo tee -a /etc/environment
fi

# ---------------------------------------------------------------------------
# 2. Memory optimisation: zSwap with lz4 compression (spec requirement)
#    On Pi Zero 2W (512 MB RAM) this prevents OOM kills without slow SD swap.
# ---------------------------------------------------------------------------
echo "Configuring zSwap + lz4 memory compression..."

# Ensure lz4 kernel modules are loaded at boot
if ! grep -q "^lz4$" /etc/modules 2>/dev/null; then
    echo "lz4" | sudo tee -a /etc/modules
fi
if ! grep -q "^lz4_compress$" /etc/modules 2>/dev/null; then
    echo "lz4_compress" | sudo tee -a /etc/modules
fi
# z3fold is a memory-efficient zpool allocator suited for 512 MB
if ! grep -q "^z3fold$" /etc/modules 2>/dev/null; then
    echo "z3fold" | sudo tee -a /etc/modules
fi

# Persist zSwap parameters via cmdline.txt (survives reboots)
if [ -f "$BOOT_CMDLINE" ] && ! grep -q "zswap.enabled=1" "$BOOT_CMDLINE"; then
    echo "Adding zswap kernel parameters to $BOOT_CMDLINE..."
    sudo sed -i 's/$/ zswap.enabled=1 zswap.compressor=lz4 zswap.zpool=z3fold/' "$BOOT_CMDLINE"
else
    echo "zswap parameters already present in $BOOT_CMDLINE (or file not found)"
fi

# Apply immediately for the current boot session (best-effort)
echo 1 | sudo tee /sys/module/zswap/parameters/enabled      > /dev/null 2>&1 || true
echo lz4 | sudo tee /sys/module/zswap/parameters/compressor > /dev/null 2>&1 || true
echo z3fold | sudo tee /sys/module/zswap/parameters/zpool   > /dev/null 2>&1 || true

# Disable disk-based swap on MicroSD (spec: avoid SD swap latency)
echo "Disabling disk-based swap (dphys-swapfile)..."
sudo systemctl stop dphys-swapfile  2>/dev/null || true
sudo systemctl disable dphys-swapfile 2>/dev/null || true

# ---------------------------------------------------------------------------
# 3. Python virtual environment and packages
# ---------------------------------------------------------------------------
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    echo "Creating virtual environment (--system-site-packages gives access to"
    echo "  system opencv and picamera2 without reinstalling them)..."
    python3 -m venv --system-site-packages venv
fi

source venv/bin/activate

pip install --upgrade pip

echo "Installing project Python dependencies..."
# opencv-python in requirements.txt is for non-Pi dev; on Pi we use the system
# package (already accessible via --system-site-packages) so skip it here.
pip install -r requirements.txt --ignore-installed opencv-python 2>/dev/null || \
    pip install -r requirements.txt

echo "Installing HandheldDietScanner package..."
pip install -e .

# ---------------------------------------------------------------------------
# 4. Systemd auto-start service
# ---------------------------------------------------------------------------
echo "Setting up auto-start service..."
sudo cp deploy/diet-scanner.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable diet-scanner.service

# ---------------------------------------------------------------------------
# 5. Directory structure and permissions
# ---------------------------------------------------------------------------
echo "Creating data directories..."
mkdir -p data/captures

echo "Setting permissions..."
sudo chown -R "$USER":"$USER" .

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "┌─────────────────────────────────────────────────────────────────┐"
echo "│  REQUIRED STEPS BEFORE FIRST USE                               │"
echo "│                                                                 │"
echo "│  1. REBOOT — activates the display driver, camera, and zSwap:  │"
echo "│       sudo reboot                                               │"
echo "│                                                                 │"
echo "│  2. CALIBRATE TOUCH (once, after reboot) — resistive screens   │"
echo "│     must be calibrated or tap coordinates will be wrong:       │"
echo "│       TSLIB_TSDEVICE=/dev/input/touchscreen \                  │"
echo "│       TSLIB_FBDEV=/dev/fb1 \                                   │"
echo "│       TSLIB_CALIBFILE=/etc/pointercal \                        │"
echo "│       sudo -E ts_calibrate                                     │"
echo "│     Follow the on-screen prompts (tap each crosshair).         │"
echo "│     This writes /etc/pointercal which the service reads.       │"
echo "│                                                                 │"
echo "│  3. START the service:                                         │"
echo "│       sudo systemctl start diet-scanner.service                │"
echo "└─────────────────────────────────────────────────────────────────┘"
echo ""
echo "Other useful commands:"
echo "  journalctl -u diet-scanner.service -f   # live logs"
echo "  sudo systemctl disable diet-scanner.service  # remove auto-start"
echo "  source venv/bin/activate && python main.py   # run manually"