"""
HandheldDietScanner - Main Application Entry Point
A modular allergen detection system for Raspberry Pi Zero 2W
"""

import argparse
import os
import pygame
import sys

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK, COLOR_WHITE,
    PREPARE_SCAN_DURATION, DEFAULT_PROFILES
)
from ui.screens import (
    HomeScreen, WaitingToScanScreen, SettingsScreen,
    AllergyProfileScreen, PreparingToScanScreen,
    LiveViewScreen, ProcessingScreen, ResultsScreen,
)
from ui.components import UserProfile as UIUserProfile
from services.profile_manager import ProfileManager, UserProfile as ServiceUserProfile
from services.scan_processor import ScanProcessor
from services.data_storage import DataStorage
from hardware.display import DisplayController
from hardware.camera import MockCamera, PiCameraInterface, CameraInterface
from hardware.sensor import MockSensor
from utils.logger import setup_logger, get_logger
from utils.power_manager import PowerManager
from utils.touch_input import TouchInputThread


class HandheldDietScanner:
    """Main application class for HandheldDietScanner"""

    def __init__(self, local: bool = False):
        self.local = local

        # Setup logging
        self.logger = setup_logger()
        self.logger.info("Initializing HandheldDietScanner (local=%s)", local)

        # Initialize services
        self.profile_manager = ProfileManager()
        self.data_storage = DataStorage()

        # In local mode use MockCamera directly so picamera2 is never imported.
        camera: CameraInterface = MockCamera() if local else PiCameraInterface()
        self.scan_processor = ScanProcessor(
            camera=camera,
            sensor=MockSensor(),
            data_storage=self.data_storage
        )

        # Initialize hardware — tell the display controller to use a normal
        # windowed SDL driver when running locally.
        self.display = DisplayController(SCREEN_WIDTH, SCREEN_HEIGHT, local=local)

        # Initialize power manager
        self.power_manager = PowerManager()
        self.power_manager.set_wake_callback(self._on_wake)
        self.power_manager.set_sleep_callback(self._on_sleep)

        # Touch input thread — only needed on Pi hardware (evdev / ADS7846).
        # In local mode SDL mouse events are used directly instead.
        if not local:
            touch_dev = os.environ.get('SDL_MOUSEDEV', '/dev/input/touchscreen')
            self.touch_thread = TouchInputThread(
                device_path=touch_dev,
                screen_w=SCREEN_WIDTH,
                screen_h=SCREEN_HEIGHT
            )
        else:
            self.touch_thread = None
        
        # Application state
        self.current_screen = None
        self.state = "HOME"
        self.profile_selected = None
        self.run = True
        # Holds the last live frame captured during the preparation countdown
        self._last_live_frame: object = None
        
        self.logger.info("HandheldDietScanner initialized successfully")
    
    def _on_wake(self):
        """Callback when system wakes from sleep"""
        self.logger.info("System waking up")
        # Restore display brightness, etc.
    
    def _on_sleep(self):
        """Callback when system enters sleep mode"""
        self.logger.info("System entering sleep mode")
        # Reduce display brightness, etc.
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                return
            
            # Record activity for power management
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self.power_manager.record_activity()
            
            # Handle screen-specific events
            if self.state == "ALLERGY":
                new_state = self.current_screen.userAction(event, self.profile_selected)
            elif self.state == "RESULTS":
                new_state = self.current_screen.userAction(event)
            else:
                new_state = self.current_screen.userAction(event)
            
            if new_state != self.state:
                self.transition_to_state(new_state, event)
    
    def transition_to_state(self, new_state: str, event=None):
        """Transition to a new application state"""
        if new_state == "HOME":
            # Stop camera if the user backed out of the live viewfinder
            if self.state == "LIVE":
                self.scan_processor.camera.stop()
            self.current_screen = self.home_screen
            self.profile_selected = None

        elif new_state == "SCAN":
            if self.state == "HOME":
                # Determine which profile was selected
                if event and hasattr(event, 'pos'):
                    if self.home_screen.profileOne.isClicked(event.pos):
                        self.profile_selected = self.home_screen.profileOne
                    elif self.home_screen.profileTwo.isClicked(event.pos):
                        self.profile_selected = self.home_screen.profileTwo

            if self.profile_selected:
                self.scan_screen.getProfile(self.profile_selected.name)
            self.current_screen = self.scan_screen

        elif new_state == "LIVE":
            self.scan_processor.camera.start()
            self.current_screen = self.live_screen

        elif new_state == "PROCESSING":
            self.processing_screen.set_frame(None)
            self.current_screen = self.processing_screen

        elif new_state == "PREPARE":
            self._last_live_frame = None
            if self.profile_selected:
                if isinstance(self.scan_processor.camera, MockCamera):
                    # No real camera: pre-load the demo image for both screens
                    profile = self.profile_manager.get_profile_by_name(self.profile_selected.name)
                    preset_image = (
                        profile.demo_scan_image if profile
                        else (
                            "ui/assets/reesesImage.jpg"
                            if self.profile_selected.name == "Bruce"
                            else "ui/assets/hershey.jpg"
                        )
                    )
                    self.preparing_screen.updateImage(preset_image)
                else:
                    # Real camera: start the stream; frames arrive in update()
                    self.scan_processor.camera.start()
                self.preparing_screen.resetTimer()
            self.current_screen = self.preparing_screen

        elif new_state == "SETTINGS":
            # Persist allergy edits when returning from the allergy editor
            if self.state == "ALLERGY" and self.profile_selected is not None:
                self.profile_manager.update_allergies(
                    self.profile_selected.name,
                    list(self.profile_selected.allergies)
                )
            self.current_screen = self.settings_screen
            
        elif new_state == "ALLERGY":
            self.current_screen = self.allergy_screen
        
        self.state = new_state
    
    def update(self):
        """Update game logic"""
        if self.state == "LIVE":
            frame = self.scan_processor.camera.get_live_frame()
            self.live_screen.update_frame(frame)

        elif self.state == "PROCESSING":
            if self.processing_screen.timer >= self.processing_screen.HOLD_FRAMES:
                self.state = "RESULTS"
                self.current_screen = self.results_screen

        elif self.state == "PREPARE":
            # Grab a live frame every tick for the Digital Loupe viewfinder
            live_frame = self.scan_processor.camera.get_live_frame()
            if live_frame is not None:
                self._last_live_frame = live_frame
                self.preparing_screen.updateSurface(live_frame)

            if self.preparing_screen.timer >= PREPARE_SCAN_DURATION:
                # Stop the camera stream, run OCR on the last captured frame,
                # and push both the image and the allergen results to ResultsScreen.
                self.scan_processor.camera.stop()
                if self.profile_selected is not None:
                    result = self.scan_processor.execute_scan(
                        profile_name=self.profile_selected.name,
                        use_camera=False,
                        frame=self._last_live_frame
                    )
                    if self._last_live_frame is not None:
                        pass  # ResultsScreen no longer uses allergens_detected
                self.state = "RESULTS"
                self.current_screen = self.results_screen

        # Check for idle/sleep
        if self.power_manager.check_idle():
            pass
    
    def render(self):
        """Render the current screen"""
        screen = self.display.get_screen()
        screen.fill(COLOR_BLACK)
        
        if self.state == "ALLERGY":
            self.current_screen.drawScreen(screen, self.profile_selected)
        else:
            self.current_screen.drawScreen(screen)
        
        # Show idle warning if about to sleep
        remaining = self.power_manager.get_remaining_idle_time()
        if 0 < remaining < 10 and not self.power_manager.is_sleeping:
            self._draw_idle_warning(screen, remaining)
        
        self.display.update_display()
    
    def _draw_idle_warning(self, screen, remaining_time: float):
        """Draw idle warning message"""
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Sleeping in {int(remaining_time)} seconds...", True, COLOR_WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 30))
    
    def _init_screens(self):
        """Initialize UI screens after display is ready"""
        self.home_screen = HomeScreen()
        self.scan_screen = WaitingToScanScreen()
        self.settings_screen = SettingsScreen()
        self.allergy_screen = AllergyProfileScreen()
        self.preparing_screen = PreparingToScanScreen()
        self.live_screen = LiveViewScreen()
        self.processing_screen = ProcessingScreen()
        self.results_screen = ResultsScreen()
        
        # Set initial screen
        self.current_screen = self.home_screen
        
        # Sync UI profiles with service profiles
        self._sync_profiles()
        
        self.logger.info("UI screens initialized")
    
    def _sync_profiles(self):
        """Sync UI profiles with profile manager data"""
        profiles = self.profile_manager.get_profiles()
        
        # Update home screen profiles
        if len(profiles) >= 2:
            # Update existing profiles
            self.home_screen.profileOne.name = profiles[0].name
            self.home_screen.profileOne.allergies = profiles[0].allergies
            self.home_screen.profileTwo.name = profiles[1].name
            self.home_screen.profileTwo.allergies = profiles[1].allergies
    
    def run_application(self):
        """Main application loop"""
        if not self.display.init_display():
            self.logger.error("Failed to initialize display")
            return False
        
        # Initialize screens after display is ready
        self._init_screens()

        # Touch input thread is only used on Pi hardware.
        if self.touch_thread is not None:
            self.touch_thread.start()

        self.logger.info("Starting main loop")
        
        while self.run:
            self.handle_events()
            self.update()
            self.render()
            self.display.tick()
        
        self.shutdown()
        return True
    
    def shutdown(self):
        """Clean shutdown"""
        self.logger.info("Shutting down HandheldDietScanner")
        if self.touch_thread is not None:
            self.touch_thread.stop()
        self.display.shutdown()
        pygame.quit()
        self.logger.info("Shutdown complete")


def main():
    """Entry point function"""
    parser = argparse.ArgumentParser(description="Handheld Diet Scanner")
    parser.add_argument(
        "--local",
        action="store_true",
        help=(
            "Run with a normal windowed display and mock camera — "
            "no Pi framebuffer or hardware camera required."
        ),
    )
    args = parser.parse_args()

    try:
        app = HandheldDietScanner(local=args.local)
        success = app.run_application()
        return 0 if success else 1
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())