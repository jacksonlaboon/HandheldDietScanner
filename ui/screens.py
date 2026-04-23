"""
Screen classes for HandheldDietScanner
"""
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK, COLOR_WHITE,
    COLOR_GREEN, COLOR_DARK_GREEN, COLOR_GRAY_BUTTON,
    COLOR_YELLOW, COLOR_RED, COLOR_LIGHT_GREEN,
    COLOR_BORDER_WARN, COLOR_BORDER_OK,
    FONT_BODY_SIZE, FONT_WARN_SIZE,
    PREPARE_SCAN_DURATION, COLOR_LIGHT_YELLOW
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
                return "PREPARE"
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


class ResultsScreen:
    """Screen displaying scan results"""
    __slots__ = [
        'bigFont', 'homeIcon', 'zoomLevel',
        'baseImage', 'displayImage', 'fullImage', 'magImage',
        'magRect', 'imgRect', 'fullRect',
        'allergens_detected',
    ]
    
    def __init__(self):
        self.bigFont = load_font(FONT_WARN_SIZE)
        self.homeIcon = HomeButton(0, 0, "ui/assets/homeIcon.png")
        
        # State: 0 = Normal, 1 = Fullscreen, 2 = Magnified
        self.zoomLevel = 0
        self.baseImage = None
        self.displayImage = None
        self.fullImage = None
        self.magImage = None
        self.magRect = None
        self.imgRect = None
        self.fullRect = None
        # Populated by main before transitioning to this screen
        self.allergens_detected: dict = {}

    def updateSurface(self, surface: pygame.Surface):
        """Populate zoom levels from a live-captured pygame Surface."""
        self.baseImage = surface.copy()
        self._build_zoom_images()

    def updateImage(self, imgPath):
        """Populate zoom levels from a file path (demo / mock mode)."""
        self.baseImage = pygame.image.load(imgPath).convert()
        self._build_zoom_images()

    def _build_zoom_images(self):
        """Pre-scale the base image for the three zoom levels."""
        
        # Standard view with text at top
        self.displayImage = pygame.transform.scale(self.baseImage, (SCREEN_WIDTH, SCREEN_HEIGHT - 60))
        self.imgRect = self.displayImage.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        
        # Fullscreen view
        self.fullImage = pygame.transform.scale(self.baseImage, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fullRect = self.fullImage.get_rect(topleft=(0, 0))
        
        # Magnified view (2x scale)
        self.magImage = pygame.transform.scale(self.baseImage, (SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2))

    def drawScreen(self, screen, profileSelected):
        """Draw results screen with appropriate zoom level"""
        if self.zoomLevel == 0:
            # Determine if any of the profile's allergens were actually detected
            profile_allergens = set(a.lower() for a in profileSelected.allergies)
            detected_allergens = {
                k for k, v in self.allergens_detected.items() if v
            }
            allergen_hit = bool(
                profile_allergens & {a.lower() for a in detected_allergens}
            ) if profile_allergens else bool(detected_allergens)

            # Spec: high-visibility Red/Green *border* indicators (not full-screen fill)
            border_color = COLOR_BORDER_WARN if allergen_hit else COLOR_BORDER_OK
            pygame.draw.rect(screen, border_color, screen.get_rect(), 8)

            self.homeIcon.drawHomeIcon(screen)
            if self.displayImage:
                screen.blit(self.displayImage, self.imgRect)

            msg_text = "ALLERGEN DETECTED!" if allergen_hit else "NO ALLERGENS"
            msg_color = COLOR_YELLOW if allergen_hit else COLOR_LIGHT_GREEN
            msg = self.bigFont.render(msg_text, True, msg_color)
            msg_x = SCREEN_WIDTH // 2 - msg.get_width() // 2
            msg_y = 15
            # Dark backing strip so the high-visibility colours stay readable on
            # the light yellow background (spec: min 7:1 contrast for all text).
            backing = pygame.Surface((msg.get_width() + 16, msg.get_height() + 8))
            backing.fill(COLOR_BLACK)
            screen.blit(backing, (msg_x - 8, msg_y - 4))
            screen.blit(msg, (msg_x, msg_y))

        elif self.zoomLevel == 1:
            # FULLSCREEN
            screen.blit(self.fullImage, self.fullRect)

        elif self.zoomLevel == 2:
            # MAGNIFIED at specific tap location
            screen.blit(self.magImage, self.magRect)

    def userAction(self, event, profileSelected):
        """Handle user interactions and zoom level changes"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.zoomLevel == 0:
                if self.imgRect.collidepoint(event.pos):
                    self.zoomLevel = 1
                    return "RESULTS"
                elif self.homeIcon.isClicked(event.pos):
                    return "HOME"
            
            elif self.zoomLevel == 1:
                # Get tap position to calculate magnification center
                tapX, tapY = event.pos
           
                self.magRect = self.magImage.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                # Calculate offset from center
                offsetX = (SCREEN_WIDTH // 2) - tapX
                offsetY = (SCREEN_HEIGHT // 2) - tapY
                
                self.magRect.centerx += offsetX * 2
                self.magRect.centery += offsetY * 2
                
                # Ensure image stays on screen
                if self.magRect.left > 0: self.magRect.left = 0
                if self.magRect.right < SCREEN_WIDTH: self.magRect.right = SCREEN_WIDTH
                if self.magRect.top > 0: self.magRect.top = 0
                if self.magRect.bottom < SCREEN_HEIGHT: self.magRect.bottom = SCREEN_HEIGHT
                
                self.zoomLevel = 2
                return "RESULTS"
            
            elif self.zoomLevel == 2:
                # Tap again to go back to normal
                self.zoomLevel = 0
                return "RESULTS"
                
        return "RESULTS"