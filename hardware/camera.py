"""
Camera interface for HandheldDietScanner
"""
import pygame
from abc import ABC, abstractmethod
from config import SCREEN_WIDTH, SCREEN_HEIGHT


class CameraInterface(ABC):
    """Abstract base class for camera hardware"""
    
    @abstractmethod
    def capture_image(self):
        """Capture image from camera and return as pygame surface"""
        pass
    
    @abstractmethod
    def get_resolution(self) -> tuple:
        """Get current resolution as (width, height)"""
        pass
    
    @abstractmethod
    def start(self):
        """Start camera capture"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop camera capture"""
        pass


class MockCamera(CameraInterface):
    """Mock camera for development without hardware"""
    
    def __init__(self):
        self.resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)
    
    def capture_image(self):
        """Return a mock image surface"""
        # Create a test pattern surface
        surface = pygame.Surface((self.resolution[0], self.resolution[1]))
        surface.fill((100, 100, 100))  # Gray background
        
        # Draw a simple test pattern
        pygame.draw.rect(surface, (255, 0, 0), (50, 50, 100, 100))  # Red square
        pygame.draw.circle(surface, (0, 255, 0), (240, 160), 50)    # Green circle
        pygame.draw.line(surface, (0, 0, 255), (0, 0), (480, 320), 5)  # Blue diagonal line
        
        return surface
    
    def get_resolution(self) -> tuple:
        """Get current resolution"""
        return self.resolution
    
    def start(self):
        """Start camera capture (no-op for mock)"""
        pass
    
    def stop(self):
        """Stop camera capture (no-op for mock)"""
        pass


class PiCameraInterface(CameraInterface):
    """Raspberry Pi Camera Module interface"""
    
    def __init__(self, resolution=(640, 480)):
        self.resolution = resolution
        self.camera = None
        self._init_camera()
    
    def _init_camera(self):
        """Initialize Pi Camera"""
        try:
            from picamera2 import Picamera2
            self.camera = Picamera2()
            
            # Configure camera for optimal performance on Pi Zero 2W
            config = self.camera.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"}
            )
            self.camera.configure(config)
            
        except ImportError:
            print("Warning: picamera2 not available, falling back to mock camera")
            self.camera = None
    
    def capture_image(self):
        """Capture image from Pi Camera"""
        if self.camera is None:
            # Fallback to mock if camera not available
            mock = MockCamera()
            return mock.capture_image()
        
        try:
            self.camera.start()
            # Capture image as numpy array and convert to pygame surface
            import numpy as np
            array = self.camera.capture_array()
            
            # Convert numpy array to pygame surface
            surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
            return surface
            
        except Exception as e:
            print(f"Camera capture error: {e}")
            # Fallback to mock
            mock = MockCamera()
            return mock.capture_image()
        finally:
            if self.camera:
                self.camera.stop()
    
    def get_resolution(self) -> tuple:
        """Get current resolution"""
        return self.resolution
    
    def start(self):
        """Start camera capture"""
        if self.camera:
            self.camera.start()
    
    def stop(self):
        """Stop camera capture"""
        if self.camera:
            self.camera.stop()