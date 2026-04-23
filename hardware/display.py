"""
Display controller for HandheldDietScanner
"""
import os
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_DEPTH, FPS


class DisplayController:
    """Manage display and touchscreen.

    Initialisation strategy (in order):
    1. Use whatever SDL_VIDEODRIVER the environment requests (fbcon by default).
    2. If that driver is unavailable (common on Pi OS Bullseye/Bookworm where
       SDL2 is compiled without fbcon), fall back to SDL_VIDEODRIVER=offscreen
       and write every rendered frame directly to the framebuffer device
       (SDL_FBDEV, default /dev/fb0).

    The offscreen path uses Surface.get_buffer().raw — a zero-copy bytes view
    of the 16-bit (RGB565) surface — which can be written straight to the
    fbtft framebuffer without numpy or any pixel conversion.
    """

    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT,
                 color_depth=COLOR_DEPTH, fps=FPS):
        self.width = width
        self.height = height
        self.color_depth = color_depth
        self.fps = fps
        self.screen = None
        self.clock = None
        self._initialized = False
        self._fb = None  # open file handle when in direct-fb mode
        self._fb_surface = None  # 16-bit conversion surface for direct-fb mode
        self._fb_path = os.environ.get('SDL_FBDEV', '/dev/fb0')

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def init_display(self) -> bool:
        """Initialise pygame display with automatic driver fallback."""
        preferred = os.environ.get('SDL_VIDEODRIVER', 'fbcon')

        if self._try_driver(preferred):
            return True

        # Preferred driver unavailable — switch to offscreen + direct fb write
        print(f"SDL driver '{preferred}' unavailable; "
              f"falling back to offscreen → {self._fb_path}")
        os.environ['SDL_VIDEODRIVER'] = 'offscreen'
        if pygame.get_init():
            pygame.quit()
        return self._try_driver('offscreen', direct_fb=True)

    def get_screen(self) -> pygame.Surface:
        if not self._initialized:
            raise RuntimeError("Display not initialized")
        return self.screen

    def get_clock(self) -> pygame.time.Clock:
        if not self._initialized:
            raise RuntimeError("Display not initialized")
        return self.clock

    def tick(self):
        if self.clock:
            self.clock.tick(self.fps)

    def update_display(self):
        if not self.screen:
            return
        if self._fb:
            # The offscreen SDL driver creates a 32-bit surface, but the fbtft
            # framebuffer is 16-bit RGB565 (480×320×2 = 307,200 bytes).
            # Blit onto a 16-bit conversion surface so the byte sizes match.
            self._fb_surface.blit(self.screen, (0, 0))
            self._fb.seek(0)
            self._fb.write(self._fb_surface.get_buffer().raw)
            self._fb.flush()
        else:
            pygame.display.flip()

    def set_fullscreen(self, fullscreen=True):
        if self.screen:
            flags = pygame.FULLSCREEN if fullscreen else 0
            self.screen = pygame.display.set_mode(
                (self.width, self.height), flags, self.color_depth
            )

    def calibrate_touch(self):
        print("Touchscreen calibration not implemented yet")
        return True

    def get_touch_input(self):
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
        if self._initialized:
            if self._fb:
                try:
                    self._fb.close()
                except Exception:
                    pass
                self._fb = None
            pygame.quit()
            self._initialized = False

    def is_initialized(self) -> bool:
        return self._initialized

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _try_driver(self, driver: str, direct_fb: bool = False) -> bool:
        """Attempt to initialise pygame with *driver*. Returns True on success."""
        try:
            os.environ['SDL_VIDEODRIVER'] = driver
            pygame.init()
            self.screen = pygame.display.set_mode(
                (self.width, self.height), 0, self.color_depth
            )
            self.clock = pygame.time.Clock()
            if direct_fb:
                self._fb = open(self._fb_path, 'wb')
                # 16-bit RGB565 surface matching the fbtft framebuffer format.
                # The offscreen driver gives us 32-bit; this is the conversion target.
                self._fb_surface = pygame.Surface(
                    (self.width, self.height), depth=16
                )
            pygame.display.set_caption("Handheld Diet Scanner")
            self._initialized = True
            print(f"Display initialised via '{driver}'"
                  + (f" → {self._fb_path}" if direct_fb else ""))
            return True
        except Exception as exc:
            print(f"Display initialization error ({driver}): {exc}")
            try:
                pygame.quit()
            except Exception:
                pass
            return False
