# HandheldDietScanner

A modular allergen detection system designed for Raspberry Pi Zero 2W integration. This application provides a touchscreen interface for managing user profiles, scanning food items for allergens, and viewing results.

## Features

- **Multi-user Support**: Create and manage multiple user profiles with individual allergy settings
- **Touchscreen Interface**: Optimized for 480x320 displays with touch input
- **Allergen Management**: Track common allergens (Milk, Eggs, Shellfish, Nuts, Wheat, Soy, Gluten, Sesame)
- **Scan Workflow**: Complete scanning workflow with preparation, capture, and results display
- **Image Zoom**: Multi-level zoom for detailed food inspection
- **Power Management**: Automatic sleep mode for battery-powered operation
- **Data Persistence**: Save profiles, scan history, and settings
- **Modular Architecture**: Easy to extend with new hardware or features

## Project Structure

```
HandheldDietScanner/
├── main.py                    # Application entry point
├── config.py                  # Configuration constants
├── requirements.txt           # Python dependencies
├── ui/                        # User Interface Layer
│   ├── __init__.py
│   ├── components.py         # Reusable UI components (buttons, profiles)
│   ├── screens.py            # Screen classes (home, scan, settings, etc.)
│   └── assets/               # Images and icons
├── hardware/                  # Hardware Abstraction Layer
│   ├── __init__.py
│   ├── camera.py             # Camera interface (Mock, PiCamera)
│   ├── sensor.py             # Allergen sensor interface
│   └── display.py            # Display controller
├── services/                  # Business Logic Layer
│   ├── __init__.py
│   ├── profile_manager.py    # User profile management
│   ├── scan_processor.py     # Scan processing logic
│   └── data_storage.py       # Data persistence
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── logger.py             # Logging system
│   └── power_manager.py      # Power management
└── tests/                     # Unit tests
    ├── __init__.py
    └── test_services.py
```

## Installation

### Prerequisites

- Python 3.7 or higher
- Raspberry Pi Zero 2W (or any Raspberry Pi)
- Pygame 2.1.0 or higher
- Touchscreen display (480x320 recommended)

### Quick Install

1. Clone the repository:
```bash
git clone <repository-url>
cd HandheldDietScanner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

### Raspberry Pi Specific Setup

For Raspberry Pi Camera support, uncomment the following in `requirements.txt`:
```
picamera2>=0.3.0
numpy>=1.20.0
```

Then install:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to customize:

- **Display Settings**: Screen resolution, FPS, color depth
- **Colors**: UI color scheme
- **File Paths**: Asset locations
- **Profiles**: Default user profiles
- **Allergens**: List of tracked allergens
- **Power Management**: Idle timeout duration

## Usage

### Basic Operation

1. **Select Profile**: Tap on a user profile from the home screen
2. **Start Scan**: Tap "START SCAN" button
3. **Wait**: System will prepare and capture image
4. **View Results**: Results displayed with allergen detection status
5. **Zoom**: Tap image to zoom, tap again to magnify, tap once more to return to normal

### Managing Allergies

1. Go to **Settings** (tap gear icon)
2. Select **Edit Allergy Profile**
3. Check/uncheck allergens for the selected user
4. Tap **Save** to confirm

### Power Management

The system automatically enters sleep mode after 5 minutes of inactivity. Tap the screen to wake.

## Development

### Running Tests

```bash
python -m pytest tests/
```

Or using unittest:
```bash
python -m unittest discover tests/
```

### Adding New Hardware

The modular architecture makes it easy to add new hardware:

1. Create a new class in `hardware/` that implements the interface
2. Update the imports in `main.py`
3. Test with the mock implementations first

Example - Adding a new camera:
```python
# hardware/my_camera.py
from hardware.camera import CameraInterface

class MyCamera(CameraInterface):
    def capture_image(self):
        # Your implementation here
        pass
```

### Adding New Allergens

Edit `config.py`:
```python
ALL_ALLERGENS = ["Milk", "Eggs", "Shellfish", "Nuts", "Wheat", "Soy", "Gluten", "Sesame", "NewAllergen"]
```

## Hardware Requirements

### Minimum

- Raspberry Pi Zero 2W
- 480x320 touchscreen display
- 8GB SD card
- Power supply

### Optional

- Raspberry Pi Camera Module
- Allergen detection sensor (spectrometer, etc.)
- Battery pack for portable operation

## Troubleshooting

### Display Issues

If the display doesn't initialize:
```bash
# Try setting SDL environment variables
export SDL_VIDEODRIVER=fbcon
python main.py
```

### Touchscreen Not Responding

Calibrate the touchscreen:
```bash
# For official Raspberry Pi display
sudo apt-get install xinput-calibrator
xinput_calibrator
```

### Performance Issues

- Reduce FPS in `config.py`
- Lower color depth to 16-bit
- Use mock camera instead of real camera during development

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Pygame community for excellent documentation
- Raspberry Pi Foundation for hardware support
- Open source contributors

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Email: [Your contact information]

## Version History

- **v1.0.0** (2024-04-21): Initial modular release
  - Complete UI refactoring
  - Hardware abstraction layer
  - Profile and data management
  - Power management system
  - Comprehensive test suite