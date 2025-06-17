import pygame
import random
from settings import (COLOR_YELLOW, COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_PURPLE, COLOR_GOLD,
                      DOUBLE_ESPRESSO_DURATION, CHEATSHEET_DURATION, SEMESTERBREAK_DURATION)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((30, 30))
        self.image.fill(COLOR_YELLOW)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = random.choice(['health', 'ammo'])
    
    def apply(self, player):
        """Wendet den PowerUp-Effekt auf den Spieler an"""
        pass  # Wird von Unterklassen überschrieben

class DoubleEspresso(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_RED)
        self.type = 'double_espresso'
    
    def apply(self, player):
        """Doppelter Espresso: Verdoppelt die Geschwindigkeit für 5 Sekunden"""
        player.double_espresso_timer = DOUBLE_ESPRESSO_DURATION
        player.is_speed_boosted = True
        player.current_speed = player.base_speed * 2
        player.score += 20  # Bonus für PowerUp-Nutzung
        print("Doppelter Espresso! Geschwindigkeit verdoppelt für 5 Sekunden!")

class CheatsheetScroll(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_BLUE)
        self.type = 'cheatsheet_scroll'
    
    def apply(self, player):
        """Spickzettel-Scroll: Friert alle Gegner für 3 Sekunden ein"""
        player.cheatsheet_timer = CHEATSHEET_DURATION
        player.enemies_frozen = True
        player.score += 30  # Bonus für PowerUp-Nutzung
        print("Spickzettel! Alle Gegner eingefroren für 3 Sekunden!")

class SemesterbreakAura(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_GREEN)
        self.type = 'semesterbreak_aura'
    
    def apply(self, player):
        """Semesterferien-Aura: Macht unverwundbar für 5 Sekunden"""
        player.semesterbreak_timer = SEMESTERBREAK_DURATION
        player.has_semesterbreak_aura = True
        player.score += 25  # Bonus für PowerUp-Nutzung
        print("Semesterferien-Aura! Unverwundbar für 5 Sekunden!")

class MotivationFishBread(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_PURPLE)
        self.type = 'motivation_fishbread'
    
    def apply(self, player):
        """Motivations-Fischbrötchen: Extra Leben"""
        player.lives += 1
        player.score += 50  # Bonus-Punkte für Extra-Leben
        print("Motivations-Fischbrötchen! +1 Leben!")

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((20, 20))
        self.image.fill(COLOR_PURPLE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = random.choice(['coin', 'gem'])

    def collect(self, player):
        """Sammelt das Collectible ein"""
        pass  # Wird von Unterklassen überschrieben

    def update(self):
        pass

class Creditpoint(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_GOLD)
        self.type = 'CP'
    
    def collect(self, player):
        """Credit Points sammeln - erhöht Score"""
        points = 10
        player.credit_points += 1
        player.score += points
        
        # Extra Leben bei bestimmten CP-Anzahlen
        if player.credit_points % 50 == 0:  # Alle 50 CP ein Extra-Leben
            player.lives += 1
            print(f"{player.credit_points} CP erreicht! Extra Leben erhalten!")

class Grade(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.image.fill(COLOR_BLUE)
        self.type = 'grade'
    
    def collect(self, player):
        """Grade (1,0-Note) sammeln - hohe Punkte und Bonusinhalte"""
        player.grades_collected += 1
        player.score += 100  # Hohe Punkte für versteckte Noten
        print(f"Note 1,0 gefunden! ({player.grades_collected} gesammelt) +100 Punkte!") 