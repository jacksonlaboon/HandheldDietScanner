"""
Hardware Abstraction Layer for HandheldDietScanner
"""
from hardware.camera import CameraInterface, MockCamera
from hardware.sensor import AllergenSensor, MockSensor
from hardware.display import DisplayController