"""
Configuration constants for HandheldDietScanner
"""

# Display Settings
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
FPS = 30
COLOR_DEPTH = 16  # 16-bit color for memory efficiency

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 150, 0)
COLOR_DARK_GREEN = (15, 109, 3)
COLOR_GRAY = (150, 150, 150)
COLOR_LIGHT_GREEN = (0, 200, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_RED = (180, 0, 0)
COLOR_GRAY_BUTTON = (100, 100, 100)

# File Paths
ASSETS_DIR = "ui/assets"
IMAGES_DIR = "ui/assets"

# Profile Images
PROFILE_IMAGE_1 = "ui/assets/mcqueen.jpeg"
PROFILE_IMAGE_2 = "ui/assets/minniemouse.jpg"

# Icon Images
HOME_ICON = "ui/assets/homeIcon.png"
SETTINGS_ICON = "ui/assets/settingsIcon.png"

# Demo Scan Images
DEMO_IMAGE_1 = "ui/assets/reesesImage.jpg"  # For Bruce (allergen detected)
DEMO_IMAGE_2 = "ui/assets/hershey.jpg"      # For Ramona (no allergens)

# UI Dimensions
PROFILE_IMAGE_SIZE = (200, 200)
ICON_SIZE = (60, 60)
BUTTON_BORDER_RADIUS = 10
CHECKBOX_SIZE = (40, 40)

# Default Profiles
DEFAULT_PROFILES = [
    {
        "name": "Bruce",
        "image": PROFILE_IMAGE_1,
        "allergies": [],
        "demo_scan_image": DEMO_IMAGE_1
    },
    {
        "name": "Ramona",
        "image": PROFILE_IMAGE_2,
        "allergies": [],
        "demo_scan_image": DEMO_IMAGE_2
    }
]

# Allergen List
ALL_ALLERGENS = ["Milk", "Eggs", "Shellfish", "Nuts", "Wheat", "Soy", "Gluten", "Sesame"]

# Timing
PREPARE_SCAN_DURATION = 60  # frames (approx 2 seconds at 30 FPS)

# Power Management
IDLE_TIMEOUT_SECONDS = 300  # 5 minutes

# Hardware Pins (for future GPIO integration)
GPIO_PINS = {
    "sensor_trigger": 17,
    "sensor_ready": 27,
    "led_indicator": 22,
    "button_scan": 23
}

# Logging
LOG_FILE = "diet_scanner.log"
LOG_LEVEL = "INFO"