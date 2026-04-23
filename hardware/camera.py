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
        """Capture a single image and return it as a pygame Surface."""
        pass

    @abstractmethod
    def get_live_frame(self):
        """Return the latest frame as a pygame Surface for the live viewfinder.

        Implementations should keep the camera running between calls so the
        ISP can offload preprocessing (spec: 30-fps Digital Loupe via ISP).
        Returns None if no frame is available yet.
        """
        pass

    @abstractmethod
    def get_resolution(self) -> tuple:
        """Get current resolution as (width, height)"""
        pass

    @abstractmethod
    def start(self):
        """Start camera streaming"""
        pass

    @abstractmethod
    def stop(self):
        """Stop camera streaming"""
        pass


class MockCamera(CameraInterface):
    """Mock camera for development without hardware"""

    def __init__(self):
        self.resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)

    def _make_test_surface(self) -> pygame.Surface:
        surface = pygame.Surface(self.resolution)
        surface.fill((100, 100, 100))
        pygame.draw.rect(surface, (255, 0, 0), (50, 50, 100, 100))
        pygame.draw.circle(surface, (0, 255, 0), (240, 160), 50)
        pygame.draw.line(surface, (0, 0, 255), (0, 0), (480, 320), 5)
        return surface

    def capture_image(self) -> pygame.Surface:
        return self._make_test_surface()

    def get_live_frame(self) -> pygame.Surface:
        """Mock live frame — identical to a still capture."""
        return self._make_test_surface()

    def get_resolution(self) -> tuple:
        return self.resolution

    def start(self):
        pass

    def stop(self):
        pass


class PiCameraInterface(CameraInterface):
    """Raspberry Pi Camera Module 2 interface (picamera2 / libcamera).

    The camera is kept *running* between `get_live_frame()` calls so the Pi's
    ISP can offload preprocessing — this is what enables the 30-fps Digital
    Loupe described in the spec without saturating the CPU.

    Capture resolution is set to 1280×960 so the OCR pre-processing step
    (resize to 800 px wide) is always a *downscale*, achieving the documented
    ~70 % complexity reduction before Tesseract processes the frame.
    """

    def __init__(self, resolution=(1280, 960)):
        self.resolution = resolution
        self.camera = None
        self._started = False
        self._mock = MockCamera()   # fallback when picamera2 is unavailable
        self._init_camera()

    def _init_camera(self):
        """Initialize the Pi Camera via picamera2."""
        try:
            from picamera2 import Picamera2
            self.camera = Picamera2()
            # Preview config is lightweight — keeps ISP pipeline alive at 30 fps
            config = self.camera.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"}
            )
            self.camera.configure(config)
        except Exception as e:
            print(f"Warning: picamera2 unavailable ({e}), using mock camera")
            self.camera = None

    def _array_to_surface(self, array) -> pygame.Surface:
        """Convert an RGB888 numpy array to a pygame Surface."""
        import numpy as np
        # picamera2 returns (h, w, 3); pygame.surfarray expects (w, h, 3)
        return pygame.surfarray.make_surface(array.swapaxes(0, 1))

    def start(self):
        """Start the camera streaming pipeline."""
        if self.camera and not self._started:
            try:
                self.camera.start()
                self._started = True
            except Exception as e:
                print(f"Camera start error: {e}")

    def stop(self):
        """Stop the camera streaming pipeline."""
        if self.camera and self._started:
            try:
                self.camera.stop()
            except Exception as e:
                print(f"Camera stop error: {e}")
            finally:
                self._started = False

    def get_live_frame(self) -> pygame.Surface:
        """Grab the latest frame for the 30-fps Digital Loupe viewfinder.

        Starts the camera automatically on first call so the caller does not
        need to manage the lifecycle.  Falls back to MockCamera if hardware is
        unavailable.
        """
        if self.camera is None:
            return self._mock.get_live_frame()
        try:
            if not self._started:
                self.start()
            array = self.camera.capture_array()
            return self._array_to_surface(array)
        except Exception as e:
            print(f"Live frame capture error: {e}")
            return self._mock.get_live_frame()

    def capture_image(self) -> pygame.Surface:
        """Capture a single still frame (starts/stops camera if needed)."""
        if self.camera is None:
            return self._mock.capture_image()
        try:
            was_started = self._started
            if not was_started:
                self.start()
            array = self.camera.capture_array()
            surface = self._array_to_surface(array)
            if not was_started:
                self.stop()
            return surface
        except Exception as e:
            print(f"Still capture error: {e}")
            return self._mock.capture_image()

    def get_resolution(self) -> tuple:
        return self.resolution