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
                    use_camera: bool = True) -> ScanResult:
        """Execute a complete scan workflow
        
        Args:
            profile_name: Name of the profile performing the scan
            use_camera: Whether to use camera for image capture
            
        Returns:
            ScanResult with detection results
        """
        try:
            # Step 1: Capture image
            if use_camera:
                image = self.camera.capture_image()
                image_path = self._save_captured_image(image, profile_name)
            else:
                image = None
                image_path = None
            
            # Step 2: Process image and detect allergens
            allergens_detected = self._detect_allergens(image)
            
            # Step 3: Create result
            result = ScanResult(
                profile_name=profile_name,
                image_path=image_path,
                allergens_detected=allergens_detected,
                timestamp=datetime.now().isoformat(),
                success=True
            )
            
            # Step 4: Save to history
            self.data_storage.save_scan_history(result.to_dict())
            
            return result
            
        except Exception as e:
            # Return error result
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
        """Detect allergens in image using sensor
        
        Args:
            image: pygame Surface with captured image
            
        Returns:
            Dictionary mapping allergen names to detection status
        """
        # Default allergen list
        allergens = {
            "Milk": False,
            "Eggs": False,
            "Shellfish": False,
            "Nuts": False,
            "Wheat": False,
            "Soy": False,
            "Gluten": False,
            "Sesame": False
        }
        
        try:
            if image is not None:
                # Use sensor to detect allergens
                sensor_results = self.sensor.scan(image)
                
                # Merge sensor results with default allergen list
                for allergen, detected in sensor_results.items():
                    if allergen in allergens:
                        allergens[allergen] = detected
                        
        except Exception as e:
            print(f"Error detecting allergens: {e}")
        
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