import pygame
import random
import os
from settings import (COLOR_YELLOW, COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_PURPLE, COLOR_GOLD,
                      COLOR_WHITE, COLOR_BLACK, DOUBLE_ESPRESSO_DURATION, CHEATSHEET_DURATION, 
                      SEMESTERBREAK_DURATION, IMAGE_FOLDER)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((30, 30))
        if sprite is None:
            self.image.fill(COLOR_YELLOW)  # Nur als Fallback
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = random.choice(['health', 'ammo'])
    
    def apply(self, player):
        """Wendet den PowerUp-Effekt auf den Spieler an"""
        pass  # Wird von Unterklassen überschrieben

class DoubleEspresso(PowerUp):
    def __init__(self, x, y):
        # Versuche das Bild zu laden
        image_path = os.path.join(IMAGE_FOLDER, "doppelter_espresso.png")
        sprite = None
        if os.path.exists(image_path):
            try:
                sprite = pygame.image.load(image_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (40, 40))  # Etwas größer für bessere Sichtbarkeit
                print(f"Espresso-Sprite geladen: {image_path}")
            except pygame.error as e:
                print(f"Fehler beim Laden des Espresso-Sprites: {e}")
                sprite = None
        else:
            print(f"Espresso-Sprite nicht gefunden: {image_path}")
        
        # Initialisiere mit None, dann setze das richtige Bild
        super().__init__(x, y, None)
        
        # Setze das richtige Bild
        if sprite is not None:
            self.image = sprite
        else:
            # Fallback: Rotes Rechteck
            self.image = pygame.Surface((40, 40))
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
        # Versuche das Bild zu laden
        image_path = os.path.join(IMAGE_FOLDER, "cheatsheet_scroll.png")
        sprite = None
        if os.path.exists(image_path):
            try:
                sprite = pygame.image.load(image_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (40, 40))  # Etwas größer für bessere Sichtbarkeit
                print(f"Cheatsheet-Scroll-Sprite geladen: {image_path}")
            except pygame.error as e:
                print(f"Fehler beim Laden des Cheatsheet-Scroll-Sprites: {e}")
                sprite = None
        else:
            print(f"Cheatsheet-Scroll-Sprite nicht gefunden: {image_path}")
        
        # Initialisiere mit None, dann setze das richtige Bild
        super().__init__(x, y, None)
        
        # Setze das richtige Bild
        if sprite is not None:
            self.image = sprite
        else:
            # Fallback: Blaues Rechteck mit Text
            self.image = pygame.Surface((40, 40))
            self.image.fill(COLOR_BLUE)
            # Text auf dem PowerUp
            font = pygame.font.Font(None, 24)
            text = font.render("CS", True, COLOR_WHITE)
            text_rect = text.get_rect(center=(20, 20))
            self.image.blit(text, text_rect)
        
        self.type = 'cheatsheet_scroll'
    
    def apply(self, player):
        """Spickzettel-Scroll: Friert alle Gegner für 3 Sekunden ein"""
        player.cheatsheet_timer = CHEATSHEET_DURATION
        player.enemies_frozen = True
        player.score += 30  # Bonus für PowerUp-Nutzung
        print("Spickzettel! Alle Gegner eingefroren für 3 Sekunden!")

class SemesterbreakAura(PowerUp):
    def __init__(self, x, y):
        # Versuche das Bild zu laden
        image_path = os.path.join(IMAGE_FOLDER, "semesterbreak_aura.png")
        sprite = None
        if os.path.exists(image_path):
            try:
                sprite = pygame.image.load(image_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (40, 40))  # Etwas größer für bessere Sichtbarkeit
                print(f"Semesterbreak-Aura-Sprite geladen: {image_path}")
            except pygame.error as e:
                print(f"Fehler beim Laden des Semesterbreak-Aura-Sprites: {e}")
                sprite = None
        else:
            print(f"Semesterbreak-Aura-Sprite nicht gefunden: {image_path}")
        
        # Initialisiere mit None, dann setze das richtige Bild
        super().__init__(x, y, None)
        
        # Setze das richtige Bild
        if sprite is not None:
            self.image = sprite
        else:
            # Fallback: Grünes Rechteck mit Text
            self.image = pygame.Surface((40, 40))
            self.image.fill(COLOR_GREEN)
            # Text auf dem PowerUp
            font = pygame.font.Font(None, 20)
            text = font.render("SB", True, COLOR_WHITE)
            text_rect = text.get_rect(center=(20, 20))
            self.image.blit(text, text_rect)
        
        self.type = 'semesterbreak_aura'
    
    def apply(self, player):
        """Semesterferien-Aura: Macht unverwundbar für 5 Sekunden"""
        player.semesterbreak_timer = SEMESTERBREAK_DURATION
        player.has_semesterbreak_aura = True
        player.score += 25  # Bonus für PowerUp-Nutzung
        print("Semesterferien-Aura! Unverwundbar für 5 Sekunden!")

class MotivationFishBread(PowerUp):
    def __init__(self, x, y):
        # Versuche das Bild zu laden
        image_path = os.path.join(IMAGE_FOLDER, "motivation_fishbread.png")
        sprite = None
        if os.path.exists(image_path):
            try:
                sprite = pygame.image.load(image_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (40, 40))  # Etwas größer für bessere Sichtbarkeit
                print(f"Motivation-Fishbread-Sprite geladen: {image_path}")
            except pygame.error as e:
                print(f"Fehler beim Laden des Motivation-Fishbread-Sprites: {e}")
                sprite = None
        else:
            print(f"Motivation-Fishbread-Sprite nicht gefunden: {image_path}")
        
        # Initialisiere mit None, dann setze das richtige Bild
        super().__init__(x, y, None)
        
        # Setze das richtige Bild
        if sprite is not None:
            self.image = sprite
        else:
            # Fallback: Lila Rechteck mit Text
            self.image = pygame.Surface((40, 40))
            self.image.fill(COLOR_PURPLE)
            # Text auf dem PowerUp
            font = pygame.font.Font(None, 18)
            text = font.render("FB", True, COLOR_WHITE)
            text_rect = text.get_rect(center=(20, 20))
            self.image.blit(text, text_rect)
        
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
        if sprite is None:
            self.image.fill(COLOR_PURPLE)  # Nur als Fallback
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = random.choice(['coin', 'gem'])

    def collect(self, player):
        """Sammelt das Collectible ein"""
        pass  # Wird von Unterklassen überschrieben

    def update(self):
        pass

class Creditpoint(Collectible):
    def __init__(self, x, y):
        # Versuche das Bild zu laden (sowohl cp.png als auch Cp.png)
        image_paths = [
            os.path.join(IMAGE_FOLDER, "cp.png"),
            os.path.join(IMAGE_FOLDER, "Cp.png")
        ]
        sprite = None
        
        for image_path in image_paths:
            if os.path.exists(image_path):
                try:
                    sprite = pygame.image.load(image_path).convert_alpha()
                    sprite = pygame.transform.scale(sprite, (30, 30))  # Etwas größer für bessere Sichtbarkeit
                    print(f"CP-Sprite geladen: {image_path}")
                    break
                except pygame.error as e:
                    print(f"Fehler beim Laden des CP-Sprites: {e}")
                    sprite = None
        
        if sprite is None:
            print("CP-Sprite nicht gefunden (cp.png oder Cp.png)")
        
        # Initialisiere mit None, dann setze das richtige Bild
        super().__init__(x, y, None)
        
        # Setze das richtige Bild
        if sprite is not None:
            self.image = sprite
        else:
            # Fallback: Goldenes Rechteck mit Text
            self.image = pygame.Surface((25, 25))
            self.image.fill(COLOR_GOLD)
            # Text auf dem Collectible
            font = pygame.font.Font(None, 18)
            text = font.render("CP", True, COLOR_BLACK)
            text_rect = text.get_rect(center=(12, 12))
            self.image.blit(text, text_rect)
        
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
        # Versuche das Bild zu laden (verschiedene Varianten)
        image_paths = [
            os.path.join(IMAGE_FOLDER, "1,0_Note.png"),
            os.path.join(IMAGE_FOLDER, "1,0_ Note.png"),
            os.path.join(IMAGE_FOLDER, "grade.png"),
            os.path.join(IMAGE_FOLDER, "note.png")
        ]
        sprite = None
        
        for image_path in image_paths:
            if os.path.exists(image_path):
                try:
                    sprite = pygame.image.load(image_path).convert_alpha()
                    sprite = pygame.transform.scale(sprite, (35, 35))  # Etwas größer für bessere Sichtbarkeit
                    print(f"Grade-Sprite geladen: {image_path}")
                    break
                except pygame.error as e:
                    print(f"Fehler beim Laden des Grade-Sprites: {e}")
                    sprite = None
        
        if sprite is None:
            print("Grade-Sprite nicht gefunden (1,0_Note.png, grade.png oder note.png)")
        
        # Initialisiere mit None, dann setze das richtige Bild
        super().__init__(x, y, None)
        
        # Setze das richtige Bild
        if sprite is not None:
            self.image = sprite
        else:
            # Fallback: Blaues Rechteck mit Text
            self.image = pygame.Surface((30, 30))
            self.image.fill(COLOR_BLUE)
            # Text für die Note
            font = pygame.font.Font(None, 20)
            text = font.render("1.0", True, COLOR_WHITE)
            text_rect = text.get_rect(center=(15, 15))
            self.image.blit(text, text_rect)
        
        self.type = 'grade'
    
    def collect(self, player):
        """Grade (1,0-Note) sammeln - hohe Punkte und Bonusinhalte"""
        player.grades_collected += 1
        player.score += 100  # Hohe Punkte für versteckte Noten
        print(f"Note 1,0 gefunden! ({player.grades_collected} gesammelt) +100 Punkte!") 