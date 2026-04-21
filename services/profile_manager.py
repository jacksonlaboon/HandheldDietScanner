"""
Profile management service for HandheldDietScanner
"""
from typing import List, Optional, Dict
from dataclasses import dataclass, field
import json
import os
from config import DEFAULT_PROFILES, ALL_ALLERGENS


@dataclass
class UserProfile:
    """User profile data class"""
    name: str
    image_path: str
    allergies: List[str] = field(default_factory=list)
    demo_scan_image: str = ""
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary"""
        return {
            "name": self.name,
            "image_path": self.image_path,
            "allergies": self.allergies,
            "demo_scan_image": self.demo_scan_image
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        """Create profile from dictionary"""
        return cls(
            name=data.get("name", ""),
            image_path=data.get("image_path", ""),
            allergies=data.get("allergies", []),
            demo_scan_image=data.get("demo_scan_image", "")
        )


class ProfileManager:
    """Manage user profiles and allergies"""
    
    def __init__(self, storage_path: str = "profiles.json"):
        self.storage_path = storage_path
        self.profiles: List[UserProfile] = []
        self._load_profiles()
    
    def _load_profiles(self):
        """Load profiles from storage or use defaults"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.profiles = [UserProfile.from_dict(p) for p in data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading profiles: {e}")
                self._load_default_profiles()
        else:
            self._load_default_profiles()
    
    def _load_default_profiles(self):
        """Load default profiles from config"""
        self.profiles = [
            UserProfile(
                name=p["name"],
                image_path=p["image"],
                allergies=p["allergies"],
                demo_scan_image=p["demo_scan_image"]
            )
            for p in DEFAULT_PROFILES
        ]
    
    def save_profiles(self):
        """Save profiles to storage"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump([p.to_dict() for p in self.profiles], f, indent=2)
        except IOError as e:
            print(f"Error saving profiles: {e}")
    
    def get_profiles(self) -> List[UserProfile]:
        """Get all profiles"""
        return self.profiles
    
    def get_profile_by_name(self, name: str) -> Optional[UserProfile]:
        """Get profile by name"""
        for profile in self.profiles:
            if profile.name.lower() == name.lower():
                return profile
        return None
    
    def add_profile(self, name: str, image_path: str, demo_scan_image: str = "") -> bool:
        """Add new user profile"""
        if self.get_profile_by_name(name):
            return False  # Profile already exists
        
        profile = UserProfile(
            name=name,
            image_path=image_path,
            allergies=[],
            demo_scan_image=demo_scan_image
        )
        self.profiles.append(profile)
        self.save_profiles()
        return True
    
    def update_allergies(self, profile_name: str, allergies: List[str]) -> bool:
        """Update allergy list for profile"""
        profile = self.get_profile_by_name(profile_name)
        if not profile:
            return False
        
        # Validate allergies against known list
        valid_allergies = [a for a in allergies if a in ALL_ALLERGENS]
        profile.allergies = valid_allergies
        self.save_profiles()
        return True
    
    def add_allergy(self, profile_name: str, allergen: str) -> bool:
        """Add single allergy to profile"""
        profile = self.get_profile_by_name(profile_name)
        if not profile:
            return False
        
        if allergen not in ALL_ALLERGENS:
            return False  # Unknown allergen
        
        if allergen not in profile.allergies:
            profile.allergies.append(allergen)
            self.save_profiles()
        return True
    
    def remove_allergy(self, profile_name: str, allergen: str) -> bool:
        """Remove allergy from profile"""
        profile = self.get_profile_by_name(profile_name)
        if not profile:
            return False
        
        if allergen in profile.allergies:
            profile.allergies.remove(allergen)
            self.save_profiles()
        return True
    
    def get_all_allergens(self) -> List[str]:
        """Get list of all known allergens"""
        return ALL_ALLERGENS
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile"""
        profile = self.get_profile_by_name(profile_name)
        if not profile:
            return False
        
        # Don't allow deleting the last profile
        if len(self.profiles) <= 1:
            return False
        
        self.profiles.remove(profile)
        self.save_profiles()
        return True