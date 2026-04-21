"""
Power management utility for HandheldDietScanner
"""
import time
from typing import Optional, Callable
from config import IDLE_TIMEOUT_SECONDS


class PowerManager:
    """Manage power consumption and idle states"""
    
    def __init__(self, idle_timeout: int = IDLE_TIMEOUT_SECONDS):
        self.idle_timeout = idle_timeout
        self.last_activity = time.time()
        self.is_sleeping = False
        self.on_wake_callback: Optional[Callable] = None
        self.on_sleep_callback: Optional[Callable] = None
    
    def record_activity(self):
        """Record user activity to reset idle timer"""
        self.last_activity = time.time()
        
        if self.is_sleeping:
            self.wake_up()
    
    def check_idle(self) -> bool:
        """Check if system should enter sleep mode
        
        Returns:
            True if system should go to sleep
        """
        if self.is_sleeping:
            return False
        
        idle_time = time.time() - self.last_activity
        if idle_time >= self.idle_timeout:
            self.enter_sleep_mode()
            return True
        
        return False
    
    def enter_sleep_mode(self):
        """Enter low-power sleep mode"""
        if self.is_sleeping:
            return
        
        self.is_sleeping = True
        
        # Execute sleep callback if set
        if self.on_sleep_callback:
            try:
                self.on_sleep_callback()
            except Exception as e:
                print(f"Error in sleep callback: {e}")
    
    def wake_up(self):
        """Wake up from sleep mode"""
        if not self.is_sleeping:
            return
        
        self.is_sleeping = False
        self.last_activity = time.time()
        
        # Execute wake callback if set
        if self.on_wake_callback:
            try:
                self.on_wake_callback()
            except Exception as e:
                print(f"Error in wake callback: {e}")
    
    def set_sleep_callback(self, callback: Callable):
        """Set callback to execute when entering sleep mode
        
        Args:
            callback: Function to call when system sleeps
        """
        self.on_sleep_callback = callback
    
    def set_wake_callback(self, callback: Callable):
        """Set callback to execute when waking from sleep
        
        Args:
            callback: Function to call when system wakes
        """
        self.on_wake_callback = callback
    
    def get_idle_time(self) -> float:
        """Get time since last activity in seconds
        
        Returns:
            Idle time in seconds
        """
        return time.time() - self.last_activity
    
    def get_remaining_idle_time(self) -> float:
        """Get remaining time before sleep mode
        
        Returns:
            Time in seconds until sleep, or 0 if already sleeping
        """
        if self.is_sleeping:
            return 0
        
        idle_time = self.get_idle_time()
        remaining = self.idle_timeout - idle_time
        return max(0, remaining)
    
    def set_idle_timeout(self, timeout: int):
        """Set the idle timeout duration
        
        Args:
            timeout: Timeout in seconds
        """
        self.idle_timeout = timeout
    
    def disable_sleep(self):
        """Temporarily disable sleep mode (e.g., during scanning)"""
        self.idle_timeout = float('inf')
    
    def enable_sleep(self, timeout: int = IDLE_TIMEOUT_SECONDS):
        """Re-enable sleep mode with specified timeout
        
        Args:
            timeout: Timeout in seconds
        """
        self.idle_timeout = timeout
    
    def reset(self):
        """Reset power manager to initial state"""
        self.last_activity = time.time()
        self.is_sleeping = False
        self.on_wake_callback = None
        self.on_sleep_callback = None