"""
Screen classes for HandheldDietScanner
"""
import os
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK, COLOR_WHITE,
    COLOR_GREEN, COLOR_DARK_GREEN, COLOR_GRAY_BUTTON,
    COLOR_YELLOW, COLOR_RED, COLOR_LIGHT_GREEN, COLOR_GRAY,
    COLOR_BORDER_WARN, COLOR_BORDER_OK,
    FONT_BODY_SIZE, FONT_WARN_SIZE,
    PREPARE_SCAN_DURATION, COLOR_LIGHT_YELLOW,
    DEMO_PROCESSED_LABEL,
)
from ui.components import UserProfile, Button, HomeButton, SettingsButton, load_font


class HomeScreen:
    """Home screen with user profile selection"""
    __slots__ = ['profileOne', 'profileTwo']
    
    def __init__(self):
        self.profileOne = UserProfile(20, 55, "Bruce", "ui/assets/mcqueen.jpeg")
        self.profileTwo = UserProfile(260, 55, "Ramona", "ui/assets/minniemouse.jpg")

    def drawScreen(self, screen):
        """Draw both profiles on screen"""
        self.profileOne.drawProfile(screen)
        self.profileTwo.drawProfile(screen)

    def userAction(self, event):
        """Handle user interactions"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.profileOne.isClicked(event.pos) or self.profileTwo.isClicked(event.pos):
                return "SCAN"
        return "HOME"


class WaitingToScanScreen:
    """Screen waiting for scan to begin"""
    __slots__ = ['scanIcon', 'settingsIcon', 'homeIcon', 'font', 'name', 'nameSurface', 'nameRect']
    
    def __init__(self):
        self.scanIcon = Button(60, 100, 360, 160, "START SCAN", COLOR_GREEN)
        self.settingsIcon = SettingsButton(SCREEN_WIDTH - 60, 0, "ui/assets/settingsIcon.png")
        self.homeIcon = HomeButton(0, 0, "ui/assets/homeIcon.png")
        self.font = load_font(FONT_BODY_SIZE)
        self.name = ""
        self.nameSurface = None
        self.nameRect = None

    def getProfile(self, profileName):
        """Set the profile name to display"""
        self.name = f"User: {profileName}"
        self.nameSurface = self.font.render(self.name, True, COLOR_BLACK)
        self.nameRect = self.nameSurface.get_rect(center=(SCREEN_WIDTH // 2, 35))

    def drawScreen(self, screen):
        """Draw all UI elements"""
        self.scanIcon.draw(screen)
        self.settingsIcon.drawSettingsIcon(screen)
        self.homeIcon.drawHomeIcon(screen)
        if self.nameSurface:
            screen.blit(self.nameSurface, self.nameRect)

    def userAction(self, event):
        """Handle user interactions"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.settingsIcon.isClicked(event.pos):
                return "SETTINGS"
            if self.homeIcon.isClicked(event.pos):
                return "HOME"
            if self.scanIcon.isClicked(event.pos):
                return "PROCESSING"
        return "SCAN"


class SettingsScreen:
    """Settings screen for device configuration"""
    __slots__ = ['font', 'settingsTitle', 'titleRect', 'backButton', 'allergyProfileButton', 'homeIcon']
    
    def __init__(self):
        self.font = load_font(FONT_BODY_SIZE)
        self.settingsTitle = self.font.render("DEVICE SETTINGS", True, COLOR_BLACK)
        self.titleRect = self.settingsTitle.get_rect(center=(SCREEN_WIDTH // 2, 35))
        
        self.backButton = Button(60, 200, 360, 80, "BACK TO SCAN", COLOR_GRAY_BUTTON)
        self.allergyProfileButton = Button(60, 100, 360, 80, "EDIT ALLERGY PROFILE", COLOR_DARK_GREEN)
        self.homeIcon = HomeButton(0, 0, "ui/assets/homeIcon.png")
   
    def drawScreen(self, screen):
        """Draw settings screen"""
        screen.blit(self.settingsTitle, self.titleRect)
        self.backButton.draw(screen)
        self.allergyProfileButton.draw(screen)
        self.homeIcon.drawHomeIcon(screen)
       
    def userAction(self, event):
        """Handle user interactions"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.allergyProfileButton.isClicked(event.pos):
                return "ALLERGY"
            elif self.backButton.isClicked(event.pos):
                return "SCAN"
            elif self.homeIcon.isClicked(event.pos):
                return "HOME"
        return "SETTINGS"


class AllergyProfileScreen:
    """Screen for editing allergy profiles"""
    __slots__ = ['titleFont', 'allergyFont', 'allAllergens', 'saveButton', 'homeIcon', 'optionsSelectedRect']
    
    def __init__(self):
        self.titleFont = load_font(FONT_BODY_SIZE)
        # Allergen labels need to meet the 24pt minimum per spec
        self.allergyFont = load_font(FONT_WARN_SIZE)
        self.allAllergens = ["Milk", "Eggs", "Shellfish", "Nuts", "Wheat", "Soy", "Gluten", "Sesame"]
        self.saveButton = Button(350, 10, 120, 50, "SAVE", COLOR_GREEN)
        self.homeIcon = HomeButton(0, 0, "ui/assets/homeIcon.png")
        self.optionsSelectedRect = []
   
    def drawScreen(self, screen, profileName):
        """Draw allergy profile screen"""
        title = self.titleFont.render(f"Editing: {profileName.name}", True, COLOR_BLACK)
        screen.blit(title, (100, 25))

        self.optionsSelectedRect = []
        for i, option in enumerate(self.allAllergens):
            column = i // 4
            row = i % 4
            xPos = 30 + (column * 240)
            yPos = 85 + (row * 55)

            checkBoxRect = pygame.Rect(xPos, yPos, 40, 40)
            self.optionsSelectedRect.append((checkBoxRect, option))

            if option in profileName.allergies:
                pygame.draw.rect(screen, COLOR_LIGHT_GREEN, checkBoxRect, border_radius=5)
            else:
                pygame.draw.rect(screen, COLOR_GRAY_BUTTON, checkBoxRect, border_radius=5)
           
            allergenText = self.allergyFont.render(option, True, COLOR_BLACK)
            screen.blit(allergenText, (xPos + 55, yPos + 5))
        self.saveButton.draw(screen)
        self.homeIcon.drawHomeIcon(screen)

    def userAction(self, event, profileName):
        """Handle user interactions"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for box, allergen in self.optionsSelectedRect:
                if not box.collidepoint(event.pos):
                    continue
                if allergen in profileName.allergies:
                    profileName.allergies.remove(allergen)
                else:
                    profileName.allergies.append(allergen)
            if self.saveButton.isClicked(event.pos):
                return "SETTINGS"
            if self.homeIcon.isClicked(event.pos):
                return "HOME"
        return "ALLERGY"


class PreparingToScanScreen:
    """Screen showing scan preparation progress"""
    __slots__ = ['font', 'text', 'timer', 'image', 'imageRect']
    
    def __init__(self):
        self.font = load_font(FONT_WARN_SIZE)
        self.text = self.font.render("PREPARING SCAN...", True, COLOR_BLACK)
        self.timer = 0
        self.image = None
        self.imageRect = None

    def updateImage(self, imgPath):
        """Update the viewfinder from a file path (demo / mock mode)."""
        baseImage = pygame.image.load(imgPath).convert()
        self.image = pygame.transform.scale(baseImage, (SCREEN_WIDTH, SCREEN_HEIGHT - 60))
        self.imageRect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))

    def updateSurface(self, surface: pygame.Surface):
        """Update the viewfinder from a live pygame Surface (Digital Loupe)."""
        self.image = pygame.transform.scale(surface, (SCREEN_WIDTH, SCREEN_HEIGHT - 60))
        self.imageRect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))

    def drawScreen(self, screen):
        """Draw preparation screen"""
        if self.image:
            screen.blit(self.image, self.imageRect)
        screen.blit(self.text, (SCREEN_WIDTH // 2 - self.text.get_width() // 2, 10))
        self.timer += 1

    def userAction(self, event):
        """Handle user interactions"""
        return "PREPARE"
    
    def resetTimer(self):
        """Reset the preparation timer"""
        self.timer = 0


class LiveViewScreen:
    """Live camera viewfinder with a CAPTURE button for the POC demo."""
    __slots__ = ['capture_btn', 'home_icon', 'live_surface', 'live_rect', 'captured_frame']

    def __init__(self):
        btn_w, btn_h = 200, 52
        self.capture_btn = Button(
            (SCREEN_WIDTH - btn_w) // 2, SCREEN_HEIGHT - btn_h - 10,
            btn_w, btn_h, "CAPTURE", COLOR_RED,
        )
        self.home_icon = HomeButton(0, 0, "ui/assets/homeIcon.png")
        self.live_surface = None
        self.live_rect = None
        self.captured_frame = None

    def update_frame(self, surface: pygame.Surface):
        """Receive the latest camera frame and scale it to fill the screen."""
        if surface is not None:
            self.live_surface = pygame.transform.scale(surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.live_rect = self.live_surface.get_rect(topleft=(0, 0))

    def drawScreen(self, screen):
        if self.live_surface:
            screen.blit(self.live_surface, self.live_rect)
        else:
            screen.fill((40, 40, 40))
        self.capture_btn.draw(screen)
        self.home_icon.drawHomeIcon(screen)

    def userAction(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.home_icon.isClicked(event.pos):
                self.captured_frame = None
                return "HOME"
            if self.capture_btn.isClicked(event.pos):
                self.captured_frame = (
                    self.live_surface.copy() if self.live_surface is not None else None
                )
                return "PROCESSING"
        return "LIVE"


class ProcessingScreen:
    """Frozen snapshot with a 'Processing...' banner; auto-advances via main update loop."""
    __slots__ = ['font', 'label', 'label_rect', 'snapshot', 'snap_rect', 'timer']

    HOLD_FRAMES = 75  # ~2.5 s at 30 fps

    def __init__(self):
        self.font = load_font(FONT_WARN_SIZE)
        self.label = self.font.render("Processing...", True, COLOR_WHITE)
        self.label_rect = self.label.get_rect(center=(SCREEN_WIDTH // 2, 34))
        self.snapshot = None
        self.snap_rect = None
        self.timer = 0

    def set_frame(self, surface: pygame.Surface):
        """Store the captured frame and reset the hold timer."""
        if surface is not None:
            self.snapshot = pygame.transform.scale(surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.snap_rect = self.snapshot.get_rect(topleft=(0, 0))
        else:
            self.snapshot = None
        self.timer = 0

    def drawScreen(self, screen):
        if self.snapshot:
            screen.blit(self.snapshot, self.snap_rect)
        backing_w = self.label.get_width() + 20
        backing_h = self.label.get_height() + 10
        backing = pygame.Surface((backing_w, backing_h))
        backing.fill(COLOR_BLACK)
        screen.blit(backing, (self.label_rect.x - 10, self.label_rect.y - 5))
        screen.blit(self.label, self.label_rect)
        self.timer += 1

    def userAction(self, event):
        return "PROCESSING"


class ResultsScreen:
    """POC demo results: processed label image left, hardcoded 'Soy detected' panel right."""

    # Left column width; right panel takes the remainder
    _IMG_W = 290
    _PANEL_X = 290
    _PANEL_W = SCREEN_WIDTH - 290   # 190 px

    __slots__ = [
        'label_img', 'label_rect',
        'soy_surf', 'soy_rect',
        'detected_surf', 'detected_rect',
        'back_btn',
        'allergen_font', 'detected_font',
    ]

    def __init__(self):
        self.allergen_font = load_font(FONT_WARN_SIZE)   # 54 px — meets ≥24 pt spec
        self.detected_font = load_font(32)

        cx = self._PANEL_X + self._PANEL_W // 2

        self.soy_surf = self.allergen_font.render("SOY", True, COLOR_RED)
        self.soy_rect = self.soy_surf.get_rect(center=(cx, 115))

        self.detected_surf = self.detected_font.render("detected", True, COLOR_BLACK)
        self.detected_rect = self.detected_surf.get_rect(center=(cx, 180))

        self.back_btn = Button(
            self._PANEL_X + 15, SCREEN_HEIGHT - 68,
            self._PANEL_W - 30, 52,
            "BACK", COLOR_GRAY_BUTTON,
        )

        self.label_img = None
        self.label_rect = None
        self._load_label()

    def _load_label(self):
        if os.path.exists(DEMO_PROCESSED_LABEL):
            base = pygame.image.load(DEMO_PROCESSED_LABEL).convert()
            self.label_img = pygame.transform.scale(base, (self._IMG_W, SCREEN_HEIGHT))
        else:
            placeholder = pygame.Surface((self._IMG_W, SCREEN_HEIGHT))
            placeholder.fill(COLOR_GRAY)
            self.label_img = placeholder
        self.label_rect = pygame.Rect(0, 0, self._IMG_W, SCREEN_HEIGHT)

    def drawScreen(self, screen, *_args):
        # Left: food label image
        screen.blit(self.label_img, self.label_rect)

        # Right: allergen panel
        panel_rect = pygame.Rect(self._PANEL_X, 0, self._PANEL_W, SCREEN_HEIGHT)
        pygame.draw.rect(screen, COLOR_LIGHT_YELLOW, panel_rect)
        pygame.draw.rect(screen, COLOR_BORDER_WARN, panel_rect, 4)

        screen.blit(self.soy_surf, self.soy_rect)
        screen.blit(self.detected_surf, self.detected_rect)
        self.back_btn.draw(screen)

    def userAction(self, event, profileSelected=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_btn.isClicked(event.pos):
                return "HOME"
        return "RESULTS"