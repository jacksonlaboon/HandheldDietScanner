"""
Display controller for HandheldDietScanner
"""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_DEPTH, FPS


class DisplayController:
    """Manage display and touchscreen"""
    
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, color_depth=COLOR_DEPTH, fps=FPS):
        self.width = width
        self.height = height
        self.color_depth = color_depth
        self.fps = fps
        self.screen = None
        self.clock = None
        self._initialized = False
    
    def init_display(self):
        """Initialize pygame display"""
        try:
            pygame.init()
            self.screen = pygame.display.set_mode(
                (self.width, self.height), 
                0, 
                self.color_depth
            )
            self.clock = pygame.time.Clock()
            self._initialized = True
            
            # Set display caption
            pygame.display.set_caption("Handheld Diet Scanner")
            
            return True
            
        except Exception as e:
            print(f"Display initialization error: {e}")
            return False
    
    def get_screen(self):
        """Get the pygame screen surface"""
        if not self._initialized:
            raise RuntimeError("Display not initialized")
        return self.screen
    
    def get_clock(self):
        """Get the pygame clock"""
        if not self._initialized:
            raise RuntimeError("Display not initialized")
        return self.clock
    
    def tick(self):
        """Tick the clock to maintain FPS"""
        if self.clock:
            self.clock.tick(self.fps)
    
    def update_display(self):
        """Update the display"""
        if self.screen:
            pygame.display.flip()
    
    def set_fullscreen(self, fullscreen=True):
        """Toggle fullscreen mode"""
        if self.screen:
            if fullscreen:
                self.screen = pygame.display.set_mode(
                    (self.width, self.height), 
                    pygame.FULLSCREEN, 
                    self.color_depth
                )
            else:
                self.screen = pygame.display.set_mode(
                    (self.width, self.height), 
                    0, 
                    self.color_depth
                )
    
    def calibrate_touch(self):
        """Calibrate touchscreen (placeholder for actual calibration)"""
        # For real implementation, this would:
        # 1. Display calibration points
        # 2. Record touch positions
        # 3. Calculate transformation matrix
        # 4. Store calibration data
        
        print("Touchscreen calibration not implemented yet")
        return True
    
    def get_touch_input(self):
        """Get touch input from pygame events"""
        touch_events = []
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                touch_events.append({
                    'type': 'touch',
                    'pos': event.pos,
                    'button': event.button
                })
        return touch_events
    
    def shutdown(self):
        """Shutdown display and cleanup"""
        if self._initialized:
            pygame.quit()
            self._initialized = False
    
    def is_initialized(self):
        """Check if display is initialized"""
        return self._initialized