"""
Screen classes for HandheldDietScanner
"""
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK, COLOR_WHITE,
    COLOR_GREEN, COLOR_DARK_GREEN, COLOR_GRAY_BUTTON,
    COLOR_YELLOW, COLOR_RED, COLOR_LIGHT_GREEN,
    PREPARE_SCAN_DURATION
)
from ui.components import UserProfile, Button, HomeButton, SettingsButton


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
        self.font = pygame.font.SysFont(None, 36)
        self.name = ""
        self.nameSurface = None
        self.nameRect = None

    def getProfile(self, profileName):
        """Set the profile name to display"""
        self.name = f"User: {profileName}"
        self.nameSurface = self.font.render(self.name, True, COLOR_WHITE)
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
        self.font = pygame.font.SysFont(None, 40)
        self.settingsTitle = self.font.render("DEVICE SETTINGS", True, COLOR_WHITE)
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
        self.titleFont = pygame.font.SysFont(None, 35)
        self.allergyFont = pygame.font.SysFont(None, 45)
        self.allAllergens = ["Milk", "Eggs", "Shellfish", "Nuts", "Wheat", "Soy", "Gluten", "Sesame"]
        self.saveButton = Button(350, 10, 120, 50, "SAVE", COLOR_GREEN)
        self.homeIcon = HomeButton(0, 0, "ui/assets/homeIcon.png")
        self.optionsSelectedRect = []
   
    def drawScreen(self, screen, profileName):
        """Draw allergy profile screen"""
        title = self.titleFont.render(f"Editing: {profileName.name}", True, COLOR_WHITE)
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
           
            allergenText = self.allergyFont.render(option, True, COLOR_WHITE)
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
        self.font = pygame.font.SysFont(None, 60)
        self.text = self.font.render("PREPARING SCAN...", True, COLOR_WHITE)
        self.timer = 0
        self.image = None
        self.imageRect = None

    def updateImage(self, imgPath):
        """Update the image to display"""
        baseImage = pygame.image.load(imgPath).convert()
        self.image = pygame.transform.scale(baseImage, (SCREEN_WIDTH, SCREEN_HEIGHT - 60))
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
    __slots__ = ['bigFont', 'homeIcon', 'zoomLevel', 'baseImage', 'displayImage', 'fullImage', 'magImage', 'magRect', 'imgRect', 'fullRect']
    
    def __init__(self):
        self.bigFont = pygame.font.SysFont(None, 45)
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

    def updateImage(self, imgPath):
        """Update the image for different zoom levels"""
        # Load original image
        self.baseImage = pygame.image.load(imgPath).convert()
        
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
            if profileSelected.name == "Bruce":
                screen.fill(COLOR_RED)
            self.homeIcon.drawHomeIcon(screen)
            if self.displayImage:
                screen.blit(self.displayImage, self.imgRect)
           
            msg_text = "ALLERGEN DETECTED!" if profileSelected.name == "Bruce" else "NO ALLERGENS"
            msg = self.bigFont.render(msg_text, True, COLOR_YELLOW if profileSelected.name == "Bruce" else COLOR_LIGHT_GREEN)
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 15))

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