"""
Scan processing service for HandheldDietScanner
"""
from typing import Dict, Optional, Any
import pygame
from dataclasses import dataclass
from datetime import datetime

from hardware.camera import CameraInterface, MockCamera
from hardware.sensor import AllergenSensor, MockSensor
from services.data_storage import DataStorage
from config import ALL_ALLERGENS

# Optional heavy deps — imported lazily so the app still runs without them
try:
    import cv2
    import numpy as np
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

try:
    import pytesseract
    _TESSERACT_AVAILABLE = True
except ImportError:
    _TESSERACT_AVAILABLE = False


def _surface_to_bgr(surface: pygame.Surface):
    """Convert a pygame Surface to an OpenCV BGR numpy array."""
    import numpy as np
    rgb = pygame.surfarray.array3d(surface)
    rgb = rgb.swapaxes(0, 1)          # pygame → (h, w, 3)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _preprocess_for_ocr(surface: pygame.Surface):
    """Apply the spec pipeline: resize → grayscale → bilateral filter → adaptive threshold.

    Resizing to 800 px width achieves the documented ~70 % complexity reduction
    before Tesseract processes the frame.
    """
    img = _surface_to_bgr(surface)

    # Resize to 800 px width while preserving aspect ratio
    h, w = img.shape[:2]
    target_w = 800
    scale = target_w / w
    img = cv2.resize(img, (target_w, int(h * scale)), interpolation=cv2.INTER_LINEAR)

    # Grayscale → bilateral filter (edge-preserving noise reduction) → adaptive threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    thresh = cv2.adaptiveThreshold(
        filtered, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11, C=2
    )
    return thresh


def _ocr_allergens(surface: pygame.Surface) -> Dict[str, bool]:
    """Run Tesseract 5 LSTM on the preprocessed frame and check for allergen keywords."""
    processed = _preprocess_for_ocr(surface)
    # --oem 1 = LSTM only (Tesseract 5); --psm 6 = assume uniform block of text
    text = pytesseract.image_to_string(processed, config="--oem 1 --psm 6")
    text_lower = text.lower()
    return {allergen: allergen.lower() in text_lower for allergen in ALL_ALLERGENS}


@dataclass
class ScanResult:
    """Result of a scan operation"""
    profile_name: str
    image_path: Optional[str]
    allergens_detected: Dict[str, bool]
    timestamp: str
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "profile": self.profile_name,
            "image_path": self.image_path,
            "allergens_detected": self.allergens_detected,
            "timestamp": self.timestamp,
            "success": self.success,
            "error_message": self.error_message
        }


class ScanProcessor:
    """Process scans using camera and sensor hardware"""
    
    def __init__(self, camera: Optional[CameraInterface] = None, 
                 sensor: Optional[AllergenSensor] = None,
                 data_storage: Optional[DataStorage] = None):
        # Use provided hardware or defaults
        self.camera = camera if camera else MockCamera()
        self.sensor = sensor if sensor else MockSensor()
        self.data_storage = data_storage if data_storage else DataStorage()
        
        # Calibrate sensor if needed
        if not self.sensor.is_ready():
            self.sensor.calibrate()
    
    def execute_scan(self, profile_name: str,
                     use_camera: bool = True,
                     frame: Optional[pygame.Surface] = None) -> 'ScanResult':
        """Execute a complete scan workflow.

        Args:
            profile_name: Name of the profile performing the scan.
            use_camera: Whether to capture a new frame from the camera.
            frame: Pre-captured pygame Surface (used when the live loupe already
                   grabbed the frame before this call).

        Returns:
            ScanResult with allergen detection results.
        """
        try:
            # Step 1: Obtain image
            if frame is not None:
                image = frame
                image_path = self._save_captured_image(image, profile_name)
            elif use_camera:
                image = self.camera.capture_image()
                image_path = self._save_captured_image(image, profile_name)
            else:
                image = None
                image_path = None

            # Step 2: Detect allergens (OCR path preferred, sensor fallback)
            allergens_detected = self._detect_allergens(image)

            # Step 3: Build result
            result = ScanResult(
                profile_name=profile_name,
                image_path=image_path,
                allergens_detected=allergens_detected,
                timestamp=datetime.now().isoformat(),
                success=True
            )

            # Step 4: Persist to history
            self.data_storage.save_scan_history(result.to_dict())

            return result

        except Exception as e:
            return ScanResult(
                profile_name=profile_name,
                image_path=None,
                allergens_detected={},
                timestamp=datetime.now().isoformat(),
                success=False,
                error_message=str(e)
            )
    
    def _save_captured_image(self, image: pygame.Surface, 
                            profile_name: str) -> Optional[str]:
        """Save captured image to file"""
        try:
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scan_{profile_name}_{timestamp}.png"
            filepath = f"data/captures/{filename}"
            
            # Ensure directory exists
            import os
            os.makedirs("data/captures", exist_ok=True)
            
            # Save image
            pygame.image.save(image, filepath)
            
            return filepath
            
        except Exception as e:
            print(f"Error saving captured image: {e}")
            return None
    
    def _detect_allergens(self, image: Optional[pygame.Surface]) -> Dict[str, bool]:
        """Detect allergens in an image surface.

        Strategy (in priority order):
        1. OpenCV + Tesseract OCR pipeline (spec requirement)
        2. Sensor-based detection (hardware fallback)
        3. All-false defaults (no-op mock)
        """
        allergens: Dict[str, bool] = {a: False for a in ALL_ALLERGENS}

        if image is None:
            return allergens

        # --- OCR path (preferred) ---
        if _CV2_AVAILABLE and _TESSERACT_AVAILABLE:
            try:
                ocr_results = _ocr_allergens(image)
                allergens.update(ocr_results)
                return allergens
            except Exception as e:
                print(f"OCR allergen detection failed, falling back to sensor: {e}")

        # --- Sensor / mock fallback ---
        try:
            sensor_results = self.sensor.scan(image)
            for allergen, detected in sensor_results.items():
                if allergen in allergens:
                    allergens[allergen] = detected
        except Exception as e:
            print(f"Sensor allergen detection failed: {e}")

        return allergens
    
    def get_scan_statistics(self, profile_name: Optional[str] = None) -> Dict:
        """Get statistics about scans
        
        Args:
            profile_name: Optional profile name to filter by
            
        Returns:
            Dictionary with scan statistics
        """
        history = self.data_storage.load_scan_history()
        
        if profile_name:
            history = [s for s in history if s.get("profile") == profile_name]
        
        total_scans = len(history)
        successful_scans = sum(1 for s in history if s.get("success", False))
        
        # Count allergen detections
        allergen_counts = {}
        for scan in history:
            if scan.get("success") and scan.get("allergens_detected"):
                for allergen, detected in scan["allergens_detected"].items():
                    if detected:
                        allergen_counts[allergen] = allergen_counts.get(allergen, 0) + 1
        
        return {
            "total_scans": total_scans,
            "successful_scans": successful_scans,
            "failed_scans": total_scans - successful_scans,
            "success_rate": successful_scans / total_scans if total_scans > 0 else 0,
            "allergen_detections": allergen_counts
        }
    
    def calibrate_sensor(self) -> bool:
        """Calibrate the allergen sensor
        
        Returns:
            True if calibration successful
        """
        try:
            self.sensor.calibrate()
            return self.sensor.is_ready()
        except Exception as e:
            print(f"Sensor calibration error: {e}")
            return False
    
    def test_hardware(self) -> Dict[str, bool]:
        """Test all hardware components
        
        Returns:
            Dictionary with test results for each component
        """
        results = {
            "camera": False,
            "sensor": False,
            "storage": False
        }
        
        # Test camera
        try:
            image = self.camera.capture_image()
            results["camera"] = image is not None
        except:
            pass
        
        # Test sensor
        try:
            test_surface = pygame.Surface((100, 100))
            self.sensor.scan(test_surface)
            results["sensor"] = True
        except:
            pass
        
        # Test storage
        try:
            self.data_storage.save_settings({"test": True})
            results["storage"] = True
        except:
            pass
        
        return results