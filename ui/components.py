"""
Reusable UI components for HandheldDietScanner
"""
import pygame
from config import (
    COLOR_WHITE, PROFILE_IMAGE_SIZE, ICON_SIZE, 
    BUTTON_BORDER_RADIUS, CHECKBOX_SIZE
)


class UserProfile:
    """Represents a user profile with image and name"""
    __slots__ = ['image', 'name', 'allergies', 'imageRect', 'nameTag', 'textRect']
    
    def __init__(self, xPos, yPos, profileName, profileImage):
        baseImage = pygame.image.load(profileImage).convert()
        self.image = pygame.transform.scale(baseImage, PROFILE_IMAGE_SIZE)
        self.name = profileName
        self.allergies = []
        self.imageRect = self.image.get_rect(topleft=(xPos, yPos))
        
        # Make nametag for image
        font = pygame.font.SysFont(None, 40)
        textSurface = font.render(self.name, True, COLOR_WHITE)
        self.nameTag = textSurface.convert_alpha()
        self.textRect = self.nameTag.get_rect(midtop=(self.imageRect.centerx, self.imageRect.bottom + 10))

    def drawProfile(self, screen):
        """Draw profile image and name tag"""
        screen.blit(self.image, self.imageRect)
        screen.blit(self.nameTag, self.textRect)

    def isClicked(self, mousePosClicked):
        """Check if profile image was clicked"""
        return self.imageRect.collidepoint(mousePosClicked)


class Button:
    """Generic rectangular button with text"""
    __slots__ = ['scanRect', 'text', 'color', 'font', 'textSurface', 'textInButton']
    
    def __init__(self, xPos, yPos, width, height, buttonTitle, color):
        self.scanRect = pygame.Rect(xPos, yPos, width, height)
        self.text = buttonTitle
        self.color = color
        self.font = pygame.font.SysFont(None, 40)
        self.textSurface = self.font.render(self.text, True, COLOR_WHITE)
        self.textInButton = self.textSurface.get_rect(center=self.scanRect.center)
     
    def draw(self, screen):
        """Draw button on screen"""
        pygame.draw.rect(screen, self.color, self.scanRect, border_radius=BUTTON_BORDER_RADIUS)
        screen.blit(self.textSurface, self.textInButton)

    def isClicked(self, mousePosClicked):
        """Check if button was clicked"""
        return self.scanRect.collidepoint(mousePosClicked)


class HomeButton:
    """Home icon button"""
    __slots__ = ['homeIcon', 'homeRect']
    
    def __init__(self, xPos, yPos, homeImage):
        baseImage = pygame.image.load(homeImage).convert_alpha()
        self.homeIcon = pygame.transform.scale(baseImage, ICON_SIZE)
        self.homeRect = self.homeIcon.get_rect(topleft=(xPos, yPos))
     
    def drawHomeIcon(self, screen):
        """Draw home icon on screen"""
        screen.blit(self.homeIcon, self.homeRect)
     
    def isClicked(self, mousePosClicked):
        """Check if home button was clicked"""
        return self.homeRect.collidepoint(mousePosClicked)


class SettingsButton:
    """Settings icon button"""
    __slots__ = ['settingsIcon', 'settingsRect']
    
    def __init__(self, xPos, yPos, settingsImage):
        baseImage = pygame.image.load(settingsImage).convert_alpha()
        self.settingsIcon = pygame.transform.scale(baseImage, ICON_SIZE)
        self.settingsRect = self.settingsIcon.get_rect(topleft=(xPos, yPos))
     
    def drawSettingsIcon(self, screen):
        """Draw settings icon on screen"""
        screen.blit(self.settingsIcon, self.settingsRect)
     
    def isClicked(self, mousePosClicked):
        """Check if settings button was clicked"""
        return self.settingsRect.collidepoint(mousePosClicked)