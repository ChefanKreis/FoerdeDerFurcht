import pygame
import random
from settings import COLOR_YELLOW, COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_PURPLE, COLOR_GOLD

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((30, 30))
        self.image.fill(COLOR_YELLOW)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = random.choice(['health', 'ammo'])

class DoubleEspresso(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_RED)
        self.type = 'double_espresso'

class CheatsheetScroll(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_BLUE)
        self.type = 'cheatsheet_scroll'

class SemesterbreakAura(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_GREEN)
        self.type = 'semesterbreak_aura'

class MotivationFishBread(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_PURPLE)
        self.type = 'motivation_fishbread'

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((20, 20))
        self.image.fill(COLOR_PURPLE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = random.choice(['coin', 'gem'])

    def collect(self, player):
        pass

    def update(self):
        pass

class Creditpoint(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_GOLD)
        self.type = 'CP'

class Grade(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_BLUE)
        self.type = 'grade' 