"""
Reusable UI components for HandheldDietScanner
"""
import os
import pygame
from config import (
    COLOR_WHITE, COLOR_BLACK, COLOR_GRAY, PROFILE_IMAGE_SIZE, ICON_SIZE,
    BUTTON_BORDER_RADIUS, CHECKBOX_SIZE,
    FONT_BODY_SIZE, OPEN_SANS_REGULAR
)


def load_font(size: int) -> pygame.font.Font:
    """Return Open Sans at *size* pixels; falls back to pygame default font."""
    if os.path.exists(OPEN_SANS_REGULAR):
        return pygame.font.Font(OPEN_SANS_REGULAR, size)
    return pygame.font.SysFont(None, size)


def _load_image_surface(path: str, size: tuple) -> pygame.Surface:
    """Load and scale an image; return a grey placeholder if file is missing."""
    if os.path.exists(path):
        base = pygame.image.load(path).convert()
    else:
        base = pygame.Surface(size)
        base.fill(COLOR_GRAY)
    return pygame.transform.scale(base, size)


def _load_icon_surface(path: str, size: tuple) -> pygame.Surface:
    """Load an RGBA icon; return a grey placeholder if file is missing."""
    if os.path.exists(path):
        base = pygame.image.load(path).convert_alpha()
    else:
        base = pygame.Surface(size, pygame.SRCALPHA)
        base.fill(COLOR_GRAY)
    return pygame.transform.scale(base, size)


class UserProfile:
    """Represents a user profile with image and name"""
    __slots__ = ['image', 'name', 'allergies', 'imageRect', 'nameTag', 'textRect']
    
    def __init__(self, xPos, yPos, profileName, profileImage):
        self.image = _load_image_surface(profileImage, PROFILE_IMAGE_SIZE)
        self.name = profileName
        self.allergies = []
        self.imageRect = self.image.get_rect(topleft=(xPos, yPos))
        
        font = load_font(FONT_BODY_SIZE)
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
        self.font = load_font(FONT_BODY_SIZE)
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
        self.homeIcon = _load_icon_surface(homeImage, ICON_SIZE)
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
        self.settingsIcon = _load_icon_surface(settingsImage, ICON_SIZE)
        self.settingsRect = self.settingsIcon.get_rect(topleft=(xPos, yPos))
     
    def drawSettingsIcon(self, screen):
        """Draw settings icon on screen"""
        screen.blit(self.settingsIcon, self.settingsRect)
     
    def isClicked(self, mousePosClicked):
        """Check if settings button was clicked"""
        return self.settingsRect.collidepoint(mousePosClicked)