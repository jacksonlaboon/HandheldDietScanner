"""
Data storage service for HandheldDietScanner
"""
import json
import os
import time
from typing import Dict, List, Optional
from datetime import datetime


class DataStorage:
    """Handle all file I/O operations"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_scan_history(self, scan_data: Dict):
        """Save scan results to history file"""
        history_file = os.path.join(self.data_dir, "scan_history.json")
        
        # Load existing history
        history = self.load_scan_history()
        
        # Add timestamp
        scan_data["timestamp"] = datetime.now().isoformat()
        
        # Append new scan
        history.append(scan_data)
        
        # Keep only last 1000 scans to save space
        if len(history) > 1000:
            history = history[-1000:]
        
        # Save updated history
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except IOError as e:
            print(f"Error saving scan history: {e}")
    
    def load_scan_history(self) -> List[Dict]:
        """Load scan history from file"""
        history_file = os.path.join(self.data_dir, "scan_history.json")
        
        if not os.path.exists(history_file):
            return []
        
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading scan history: {e}")
            return []
    
    def get_scan_history(self, profile_name: Optional[str] = None, 
                        limit: int = 50) -> List[Dict]:
        """Get recent scan history, optionally filtered by profile"""
        history = self.load_scan_history()
        
        if profile_name:
            history = [s for s in history if s.get("profile") == profile_name]
        
        # Return most recent scans first
        return history[-limit:][::-1]
    
    def save_settings(self, settings: Dict):
        """Save application settings"""
        settings_file = os.path.join(self.data_dir, "settings.json")
        
        try:
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self) -> Dict:
        """Load application settings"""
        settings_file = os.path.join(self.data_dir, "settings.json")
        
        if not os.path.exists(settings_file):
            return self._default_settings()
        
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                defaults = self._default_settings()
                defaults.update(settings)
                return defaults
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings: {e}")
            return self._default_settings()
    
    def _default_settings(self) -> Dict:
        """Return default settings"""
        return {
            "brightness": 100,
            "volume": 50,
            "auto_shutdown_minutes": 5,
            "fullscreen_mode": True,
            "sound_enabled": True,
            "vibration_enabled": True
        }
    
    def save_calibration_data(self, calibration_data: Dict):
        """Save sensor calibration data"""
        cal_file = os.path.join(self.data_dir, "calibration.json")
        
        try:
            with open(cal_file, 'w') as f:
                json.dump(calibration_data, f, indent=2)
        except IOError as e:
            print(f"Error saving calibration data: {e}")
    
    def load_calibration_data(self) -> Optional[Dict]:
        """Load sensor calibration data"""
        cal_file = os.path.join(self.data_dir, "calibration.json")
        
        if not os.path.exists(cal_file):
            return None
        
        try:
            with open(cal_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading calibration data: {e}")
            return None
    
    def clear_data(self):
        """Clear all stored data (use with caution)"""
        try:
            if os.path.exists(self.data_dir):
                for file in os.listdir(self.data_dir):
                    file_path = os.path.join(self.data_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        except IOError as e:
            print(f"Error clearing data: {e}")
    
    def get_storage_stats(self) -> Dict:
        """Get storage usage statistics"""
        stats = {
            "total_scans": 0,
            "total_size_bytes": 0,
            "oldest_scan": None,
            "newest_scan": None
        }
        
        history = self.load_scan_history()
        stats["total_scans"] = len(history)
        
        if history:
            stats["oldest_scan"] = history[0].get("timestamp")
            stats["newest_scan"] = history[-1].get("timestamp")
        
        # Calculate total size
        try:
            if os.path.exists(self.data_dir):
                stats["total_size_bytes"] = sum(
                    os.path.getsize(os.path.join(self.data_dir, f))
                    for f in os.listdir(self.data_dir)
                    if os.path.isfile(os.path.join(self.data_dir, f))
                )
        except OSError:
            pass
        
        return stats