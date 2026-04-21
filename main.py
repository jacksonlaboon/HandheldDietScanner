import pygame
import os

width, height = 480, 320 # 480 x 320
fps = 30 # reduce number of times ran, save power
backgroundColor = (0, 0, 0) # like a navy color
whiteColor = (255, 255, 255)

class UserProfile:
  def __init__(self, xPos, yPos, profileName, profileImage):
    baseImage = pygame.image.load(profileImage).convert() # convert to be 16 bit color
    self.image = pygame.transform.scale(baseImage, (200, 200)) # make both images same size
    self.name = profileName
    self.allergies = []
    self.imageRect = self.image.get_rect(topleft=(xPos, yPos)) # place image in desired spot
    # make nametag for image
    font = font = pygame.font.SysFont(None, 40) # default 40 pt font
    textSurface = font.render(self.name, True, whiteColor)
    self.nameTag = textSurface.convert_alpha() # make text box an image
    self.textRect = self.nameTag.get_rect(midtop=(self.imageRect.centerx, self.imageRect.bottom + 10))

  def drawProfile(self, screen):
    # draw image + name tag
    screen.blit(self.image, self.imageRect)
    screen.blit(self.nameTag, self.textRect)

  def isClicked(self, mousePosClicked):
    return self.imageRect.collidepoint(mousePosClicked)
  
class HomeScreen:
  def __init__(self):
    self.profileOne = UserProfile(20, 55, "Bruce", "images/mcqueen.jpeg") # make profile 1
    self.profileTwo = UserProfile(260, 55, "Ramona", "images/minniemouse.jpg") # make profile 2

  def drawScreen(self, screen):
    # draw both profiles
    self.profileOne.drawProfile(screen)
    self.profileTwo.drawProfile(screen)

  def userAction(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN: # if tap on screen
      if self.profileOne.isClicked(event.pos) or self.profileTwo.isClicked(event.pos):
        return "SCAN" # new state 
    return "HOME" # original state
  
class WaitingToScanScreen: 
  def __init__(self):
    self.scanIcon = Button(60, 100, 360, 160, "START SCAN", (0, 150, 0)) # scan button
    self.settingsIcon = SettingsButton(width - 60, 0, "images/settingsIcon.png")
    self.homeIcon = HomeButton(0, 0, "images/homeIcon.png")
    self.font = pygame.font.SysFont(None, 36) # make font for profile name User: XX

  def getProfile(self, profileName):
    self.name = f"User: {profileName}"
    self.nameSurface = self.font.render(self.name, True, whiteColor)
    self.nameRect = self.nameSurface.get_rect(center=(width // 2, 35)) # place at top middle
  
  def drawScreen(self, screen):
    self.scanIcon.draw(screen) # draw all icons
    self.settingsIcon.drawSettingsIcon(screen)
    self.homeIcon.drawHomeIcon(screen)
    screen.blit(self.nameSurface, self.nameRect)

  def userAction(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN: # for which icon clicked, else do nothhing and return SCAN
      if self.settingsIcon.isClicked(event.pos): 
        return "SETTINGS"
      if self.homeIcon.isClicked(event.pos):
        return "HOME"
      if self.scanIcon.isClicked(event.pos):
        return "PREPARE"
    return "SCAN"
  
class SettingsButton: 
  def __init__(self, xPos, yPos, settingsImage):
    baseImage = pygame.image.load(settingsImage).convert_alpha() # alpha b/c transparent
    self.settingsIcon = pygame.transform.scale(baseImage, (60, 60))
    self.settingsRect = self.settingsIcon.get_rect(topleft=(xPos, yPos))
    
  def drawSettingsIcon(self, screen):
    screen.blit(self.settingsIcon, self.settingsRect)
    
  def isClicked(self, mousePosClicked):
    return self.settingsRect.collidepoint(mousePosClicked)
  
class HomeButton:
  def __init__(self, xPos, yPos, homeImage):
    # same logic as settings button just diff image
    baseImage = pygame.image.load(homeImage).convert_alpha()
    self.homeIcon = pygame.transform.scale(baseImage, (60, 60))
    self.homeRect = self.homeIcon.get_rect(topleft=(xPos, yPos))
    
  def drawHomeIcon(self, screen):
    screen.blit(self.homeIcon, self.homeRect)
    
  def isClicked(self, mousePosClicked):
    return self.homeRect.collidepoint(mousePosClicked)
  
class Button:
  def __init__(self, xPos, yPos, width, height, buttonTitle, color):
    # general button that is a shape, not an image
    self.scanRect = pygame.Rect(xPos, yPos, width, height)
    self.text= buttonTitle # given text
    self.color = color
    self.font = pygame.font.SysFont(None, 40)
    self.textSurface = self.font.render(self.text, True, whiteColor)
    self.textInButton = self.textSurface.get_rect(center=self.scanRect.center)
     
  def draw(self, screen):
    pygame.draw.rect(screen, self.color, self.scanRect, border_radius=10)
    screen.blit(self.textSurface, self.textInButton)

  def isClicked(self, mousePosClicked):
    return self.scanRect.collidepoint(mousePosClicked)

class SettingsScreen:
  def __init__(self):
    self.font = pygame.font.SysFont(None, 40)
    self.settingsTitle = self.font.render("DEVICE SETTINGS", True, whiteColor)
    self.titleRect = self.settingsTitle.get_rect(center=(width // 2, 35))

    self.backButton = Button(60, 200, 360, 80, "BACK TO SCAN", (100, 100, 100))
    self.allergyProfileButton = Button(60, 100, 360, 80, "EDIT ALLERGY PROFILE", (15, 109, 3))
    self.homeIcon = HomeButton(0, 0, "images/homeIcon.png")
  
  def drawScreen(self, screen):
    screen.blit(self.settingsTitle, self.titleRect)
    self.backButton.draw(screen)
    self.allergyProfileButton.draw(screen)
    self.homeIcon.drawHomeIcon(screen)
      
  def userAction(self, event):
    if event.type ==  pygame.MOUSEBUTTONDOWN:
      if self.allergyProfileButton.isClicked(event.pos):
        return "ALLERGY"
      elif self.backButton.isClicked(event.pos):
        return "SCAN"
      elif self.homeIcon.isClicked(event.pos):
        return "HOME"
    return "SETTINGS"    

class AllergyProfileScreen:
  def __init__(self):
    self.titleFont = pygame.font.SysFont(None, 35)
    self.allergyFont = pygame.font.SysFont(None, 45)
    self.allAllergens = ["Milk", "Eggs", "Shellfish", "Nuts", "Wheat", "Soy", "Gluten", "Sesame"]
    self.saveButton = Button(350, 10, 120, 50, "SAVE", (0, 150, 0))
    self.homeIcon = HomeButton(0, 0, "images/homeIcon.png")
  
  def drawScreen(self, screen, profileName):
    title = self.titleFont.render(f"Editing: {profileName.name}", True, whiteColor)
    screen.blit(title, (100, 25))

    self.optionsSelectedRect = []
    for i, option in enumerate(self.allAllergens):
      column = i // 4 # first 4 allergens on left, other 4 on right
      row = i % 4
      xPos = 30 + (column * 240)
      yPos = 85 + (row * 55)

      checkBoxRect = pygame.Rect(xPos, yPos, 40, 40)
      self.optionsSelectedRect.append((checkBoxRect, option))

      if option in profileName.allergies:
        pygame.draw.rect(screen, (0, 200, 0), checkBoxRect, border_radius=5)
      else:
        pygame.draw.rect(screen, (150, 150, 150), checkBoxRect, border_radius=5)
      
      allergenText = self.allergyFont.render(option, True, whiteColor)
      screen.blit(allergenText, (xPos + 55, yPos + 5))
    self.saveButton.draw(screen)
    self.homeIcon.drawHomeIcon(screen)

  def userAction(self, event, profileName):
    if event.type == pygame.MOUSEBUTTONDOWN:
      for box, allergen in self.optionsSelectedRect:
        if not box.collidepoint(event.pos):
          continue
        if allergen in profileName.allergies:
          profileName.allergies.remove((allergen))
        else:
          profileName.allergies.append(allergen)
      if self.saveButton.isClicked(event.pos):
        return "SETTINGS"
      if self.homeIcon.isClicked(event.pos):
        return "HOME"
    return "ALLERGY"
  
class PreparingToScanScreen:
  def __init__(self):
    self.font = pygame.font.SysFont(None, 60)
    self.text = self.font.render("PREPARING SCAN...", True, whiteColor)
    self.timer = 0
    self.image = None
    self.imageRect = None

  def updateImage(self, imgPath):
    baseImage = pygame.image.load(imgPath).convert()
    self.image = pygame.transform.scale(baseImage, (480, height - 60))
    self.imageRect = self.image.get_rect(midbottom=(width // 2, height))
  
  def drawScreen(self, screen):
    if self.image:
      screen.blit(self.image, self.imageRect)
    screen.blit(self.text, (width // 2 - self.text.get_width() // 2, 10))
    self.timer += 1

  def userAction(self, event):
    return "PREPARE"
  def resetTimer(self):
    self.timer = 0

class ResultsScreen:
  def __init__(self):
    self.bigFont = pygame.font.SysFont(None, 45)
    self.homeIcon = HomeButton(0, 0, "images/homeIcon.png")
    
    # State: 0 = Normal, 1 = Fullscreen, 2 = Magnified
    self.zoomLevel = 0 
    self.baseImage = None 
    self.displayImage = None
    self.fullImage = None
    self.magImage = None
    self.magRect = None

  def updateImage(self, imgPath):
    # load orig image
    self.baseImage = pygame.image.load(imgPath).convert()
    
    # standard view of image, with text at top
    self.displayImage = pygame.transform.scale(self.baseImage, (480, height - 60))
    self.imgRect = self.displayImage.get_rect(midbottom=(width // 2, height))
    
    # fullscreen view of image, fills screen
    self.fullImage = pygame.transform.scale(self.baseImage, (480, 320))
    self.fullRect = self.fullImage.get_rect(topleft=(0, 0))
    
    # 4. magnify image, size is now 960 x 640
    self.magImage = pygame.transform.scale(self.baseImage, (960, 640))

  def drawScreen(self, screen, profileSelected):
    if self.zoomLevel == 0:
      if profileSelected.name == "Bruce":
        screen.fill((180, 0, 0))
      self.homeIcon.drawHomeIcon(screen)
      if self.displayImage:
        screen.blit(self.displayImage, self.imgRect)
      
      msg_text = "ALLERGEN DETECTED!" if profileSelected.name == "Bruce" else "NO ALLERGENS"
      msg = self.bigFont.render(msg_text, True, (255, 255, 0) if profileSelected.name == "Bruce" else (0, 255, 0))
      screen.blit(msg, (width // 2 - msg.get_width() // 2, 15))

    elif self.zoomLevel == 1:
      # FULLSCREEN
      screen.blit(self.fullImage, self.fullRect)

    elif self.zoomLevel == 2:
      # MAGNIFIED at specific tap location
      screen.blit(self.magImage, self.magRect)

  def userAction(self, event, profileSelected):
    if event.type == pygame.MOUSEBUTTONDOWN:
      if self.zoomLevel == 0:
        if self.imgRect.collidepoint(event.pos):
          self.zoomLevel = 1
          return "RESULTS"
        elif self.homeIcon.isClicked(event.pos):
          return "HOME"
      
      elif self.zoomLevel == 1:
        # get two pos to edit x and y
        tapX, tapY = event.pos
      
        self.magRect = self.magImage.get_rect(center=(width // 2, height // 2))
        #calculates how far away finger is from center of screen
        # width //2 = 240, if tap at 100,. offetX is 140. finger is 140 pixels to left of center, image must be pulled 140 to right
        offsetX = (width // 2) - tapX
        offsetY = (height // 2) - tapY
        
        self.magRect.centerx += offsetX * 2
        self.magRect.centery += offsetY * 2
        
        # make sure image is fully on screen, only show imagw when zoom
        if self.magRect.left > 0: self.magRect.left = 0
        if self.magRect.right < width: self.magRect.right = width
        if self.magRect.top > 0: self.magRect.top = 0
        if self.magRect.bottom < height: self.magRect.bottom = height
        
        self.zoomLevel = 2
        return "RESULTS"
      
      elif self.zoomLevel == 2:
        # Tap again to go back to normal
        self.zoomLevel = 0
        return "RESULTS"
        
    return "RESULTS"

def main():
  pygame.init()
  screen = pygame.display.set_mode((width, height), 0, 16) # 16 bits for color b/c 65k colors
  clock = pygame.time.Clock()

  homeScreen = HomeScreen()
  scanScreen = WaitingToScanScreen() 
  settingsScreen = SettingsScreen()
  allergyScreen = AllergyProfileScreen()
  preparingScanScreen = PreparingToScanScreen()
  resultsScreen = ResultsScreen()

  currentScreen = homeScreen
  state = "HOME"
  profileSelected = None

  run = True

  while run:
    if state == "PREPARE":
        if currentScreen.timer>= 60 :
          state = "RESULTS"
          currentScreen = resultsScreen

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
      
      if state == "ALLERGY" or state == "RESULTS":
        newState = currentScreen.userAction(event, profileSelected)
      else:
         newState = currentScreen.userAction(event)

      if newState != state: 
        if newState == "HOME":
          currentScreen =  homeScreen
        elif newState == "SCAN":
          if state == "HOME":
            if homeScreen.profileOne.isClicked(event.pos):
              profileSelected = homeScreen.profileOne
            else:
              profileSelected = homeScreen.profileTwo
            scanScreen.getProfile(profileSelected.name)
          if profileSelected:
            scanScreen.getProfile(profileSelected.name)
          currentScreen =  scanScreen
        elif newState == "PREPARE":
          if profileSelected.name == "Bruce":
            presetImage = "images/reesesImage.jpg"
          else:
            presetImage = "images/hershey.jpg"
          preparingScanScreen.updateImage(presetImage)
          resultsScreen.updateImage(presetImage)
          preparingScanScreen.resetTimer()
          currentScreen = preparingScanScreen
        elif newState == "SETTINGS":
          currentScreen = settingsScreen
        elif newState == "ALLERGY":
          currentScreen = allergyScreen
        state = newState
 
    screen.fill(backgroundColor) # draw background and user profiles
    if state == "ALLERGY" or state == "RESULTS": 
      currentScreen.drawScreen(screen, profileSelected)
    else:
      currentScreen.drawScreen(screen)
    
    pygame.display.flip()
    clock.tick(fps)
  
  pygame.quit()
  
if __name__ == "__main__":  
  main()