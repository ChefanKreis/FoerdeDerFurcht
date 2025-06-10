import pygame
from settings import COLOR_PLATFORM

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(COLOR_PLATFORM)
        self.rect = self.image.get_rect(topleft=(x, y))
    
    #TODO: Plattform-Logik (Bewegung, Kollision) 