"""
Unit tests for services module
"""
import unittest
import os
import json
import tempfile
import shutil
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.profile_manager import ProfileManager, UserProfile
from services.data_storage import DataStorage
from services.scan_processor import ScanProcessor, ScanResult
from config import ALL_ALLERGENS, DEFAULT_PROFILES


class TestProfileManager(unittest.TestCase):
    """Test ProfileManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.test_storage_path = os.path.join(self.test_dir, "test_profiles.json")
        self.profile_manager = ProfileManager(storage_path=self.test_storage_path)
    
    def tearDown(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir)
    
    def test_load_default_profiles(self):
        """Test that default profiles are loaded"""
        profiles = self.profile_manager.get_profiles()
        self.assertEqual(len(profiles), 2)
        self.assertEqual(profiles[0].name, "Bruce")
        self.assertEqual(profiles[1].name, "Ramona")
    
    def test_get_profile_by_name(self):
        """Test retrieving profile by name"""
        profile = self.profile_manager.get_profile_by_name("Bruce")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "Bruce")
    
    def test_get_profile_by_name_case_insensitive(self):
        """Test case-insensitive profile lookup"""
        profile = self.profile_manager.get_profile_by_name("bruce")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "Bruce")
    
    def test_add_allergy(self):
        """Test adding allergy to profile"""
        result = self.profile_manager.add_allergy("Bruce", "Nuts")
        self.assertTrue(result)
        
        profile = self.profile_manager.get_profile_by_name("Bruce")
        self.assertIn("Nuts", profile.allergies)
    
    def test_remove_allergy(self):
        """Test removing allergy from profile"""
        # First add an allergy
        self.profile_manager.add_allergy("Bruce", "Milk")
        
        # Then remove it
        result = self.profile_manager.remove_allergy("Bruce", "Milk")
        self.assertTrue(result)
        
        profile = self.profile_manager.get_profile_by_name("Bruce")
        self.assertNotIn("Milk", profile.allergies)
    
    def test_get_all_allergens(self):
        """Test getting list of all allergens"""
        allergens = self.profile_manager.get_all_allergens()
        self.assertEqual(len(allergens), 8)
        self.assertIn("Milk", allergens)
        self.assertIn("Nuts", allergens)
    
    def test_save_and_load_profiles(self):
        """Test saving and loading profiles"""
        # Modify a profile
        self.profile_manager.add_allergy("Bruce", "Eggs")
        self.profile_manager.save_profiles()
        
        # Create new profile manager and load
        new_manager = ProfileManager(storage_path=self.test_storage_path)
        profile = new_manager.get_profile_by_name("Bruce")
        self.assertIn("Eggs", profile.allergies)


class TestDataStorage(unittest.TestCase):
    """Test DataStorage functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.data_storage = DataStorage(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir)
    
    def test_save_and_load_settings(self):
        """Test saving and loading settings"""
        settings = {"brightness": 80, "volume": 60}
        self.data_storage.save_settings(settings)
        
        loaded_settings = self.data_storage.load_settings()
        self.assertEqual(loaded_settings["brightness"], 80)
        self.assertEqual(loaded_settings["volume"], 60)
    
    def test_default_settings(self):
        """Test default settings are returned when no settings exist"""
        settings = self.data_storage.load_settings()
        self.assertIn("brightness", settings)
        self.assertIn("volume", settings)
    
    def test_save_and_load_scan_history(self):
        """Test saving and loading scan history"""
        scan_data = {
            "profile": "Bruce",
            "allergens_detected": {"Nuts": True, "Milk": False},
            "success": True
        }
        
        self.data_storage.save_scan_history(scan_data)
        history = self.data_storage.load_scan_history()
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["profile"], "Bruce")
        self.assertTrue(history[0]["allergens_detected"]["Nuts"])
    
    def test_get_scan_history_filtered(self):
        """Test getting filtered scan history"""
        # Add scans for different profiles
        self.data_storage.save_scan_history({"profile": "Bruce", "success": True})
        self.data_storage.save_scan_history({"profile": "Ramona", "success": True})
        
        # Filter by profile
        bruce_scans = self.data_storage.get_scan_history(profile_name="Bruce")
        self.assertEqual(len(bruce_scans), 1)
        self.assertEqual(bruce_scans[0]["profile"], "Bruce")


class TestScanProcessor(unittest.TestCase):
    """Test ScanProcessor functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.data_storage = DataStorage(data_dir=self.test_dir)
        self.scan_processor = ScanProcessor(data_storage=self.data_storage)
    
    def tearDown(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir)
    
    def test_execute_scan_success(self):
        """Test successful scan execution"""
        result = self.scan_processor.execute_scan("Bruce", use_camera=False)
        
        self.assertTrue(result.success)
        self.assertEqual(result.profile_name, "Bruce")
        self.assertIsInstance(result.allergens_detected, dict)
    
    def test_scan_result_to_dict(self):
        """Test converting scan result to dictionary"""
        result = ScanResult(
            profile_name="TestUser",
            image_path=None,
            allergens_detected={"Milk": False},
            timestamp="2024-01-01T00:00:00",
            success=True
        )
        
        result_dict = result.to_dict()
        self.assertEqual(result_dict["profile"], "TestUser")
        self.assertTrue(result_dict["success"])
    
    def test_get_scan_statistics(self):
        """Test getting scan statistics"""
        # Execute some scans
        self.scan_processor.execute_scan("Bruce", use_camera=False)
        self.scan_processor.execute_scan("Bruce", use_camera=False)
        
        stats = self.scan_processor.get_scan_statistics("Bruce")
        
        self.assertEqual(stats["total_scans"], 2)
        self.assertEqual(stats["successful_scans"], 2)


class TestHardware(unittest.TestCase):
    """Test hardware interfaces"""
    
    def test_mock_camera_capture(self):
        """Test mock camera image capture"""
        import pygame
        from hardware.camera import MockCamera
        
        camera = MockCamera()
        image = camera.capture_image()
        
        self.assertIsNotNone(image)
        self.assertIsInstance(image, pygame.Surface)
    
    def test_mock_sensor_scan(self):
        """Test mock sensor allergen detection"""
        import pygame
        from hardware.sensor import MockSensor
        
        sensor = MockSensor()
        sensor.calibrate()
        
        test_surface = pygame.Surface((100, 100))
        results = sensor.scan(test_surface)
        
        self.assertIsInstance(results, dict)
        self.assertIn("Milk", results)
        self.assertIn("Nuts", results)
    
    def test_mock_sensor_calibration(self):
        """Test mock sensor calibration"""
        from hardware.sensor import MockSensor
        
        sensor = MockSensor()
        self.assertFalse(sensor.is_ready())
        
        sensor.calibrate()
        self.assertTrue(sensor.is_ready())


class TestPowerManager(unittest.TestCase):
    """Test PowerManager functionality"""
    
    def test_record_activity(self):
        """Test recording user activity"""
        from utils.power_manager import PowerManager
        
        pm = PowerManager(idle_timeout=1)
        pm.record_activity()
        
        # Should not be sleeping after activity
        self.assertFalse(pm.is_sleeping)
    
    def test_idle_timeout(self):
        """Test idle timeout triggers sleep"""
        from utils.power_manager import PowerManager
        import time
        
        pm = PowerManager(idle_timeout=0.1)
        pm.record_activity()
        
        # Wait for timeout
        time.sleep(0.2)
        pm.check_idle()
        
        self.assertTrue(pm.is_sleeping)
    
    def test_wake_from_sleep(self):
        """Test waking from sleep mode"""
        from utils.power_manager import PowerManager
        
        pm = PowerManager(idle_timeout=0.1)
        pm.enter_sleep_mode()
        self.assertTrue(pm.is_sleeping)
        
        pm.wake_up()
        self.assertFalse(pm.is_sleeping)


if __name__ == "__main__":
    unittest.main()