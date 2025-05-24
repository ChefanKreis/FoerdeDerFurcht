#########################################################################
# Import:     Alle Abhängigkeiten werden am Anfang eingebunden
#########################################################################

import pygame   # die Spiele-Engine
import random   # Zufallszahlen brauchen wir immer...
import os       # Das Dateisystem
import sys      # Systemfunktionen

#########################################################################
# Settings:   Hier stehen alle Konstanten Variablen für das Spiel.
#             Diese könnten auch ausgelagert werden in settings.py
#             und per import eingebunden werden
#########################################################################

WIDTH = 800       # Breite des Bildschirms in Pixeln
HEIGHT = 600       # Höhe des Bildschirms in Pixeln
FPS = 60        # Frames per Second (30 oder 60 FPS sind üblicher Standard)
GRAVITY = 0.8   # Schwerkraftskonstante

#########################################################################
# Initialisierung:    pygame wird gestartet
#                     und eine Bildschirm-Ausgabe wird generiert
#########################################################################

pygame.init()           # pygame Initialisierung
pygame.mixer.init()     # Die Sound-Ausgabe wird initialisiert
pygame.display.set_caption("My Game")   # Überschrift des Fensters

#########################################################################
# Das Clock-Objekt:    Damit lassen sich Frames und Zeiten messen
#                      Sehr wichtig für Animationen etc.
#########################################################################

clock = pygame.time.Clock()

#########################################################################
# Das screen-Objekt:    Auf dem screen werden alle Grafiken gerendert
# Cooles Feature: pygame.SCALED(verdoppelte Auflösung für einen Retro-Effekt)
#########################################################################

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)

#########################################################################
# Grafiken:    Das Einbinden von Grafiken kann auch ausgelagert werden
#########################################################################

# Das Dateisystem ermittelt das aktuelle Verzeichnis
game_folder = os.path.dirname(__file__)

# Wir binden eine Grafik (Ball) ein
# convert_alpha lässt eine PNG-Datei transparent erscheinen
# ball = pygame.image.load(os.path.join(game_folder, 'ball.png')).convert_alpha()
# imageRect = ball.get_rect()

#########################################################################
# Klassen: Spielfiguren, Gegner, PowerUps
#########################################################################

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Klausur Chaos: Die Förde der Furcht")
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_level = Level(1)
        self.score = 0

    def start(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.current_level.player.velocity.x = -5
                if event.key == pygame.K_RIGHT:
                    self.current_level.player.velocity.x = 5
                if event.key == pygame.K_UP:
                    self.current_level.player.jump()
                if event.key == pygame.K_SPACE:
                    self.current_level.player.shoot()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and self.current_level.player.velocity.x < 0:
                    self.current_level.player.velocity.x = 0
                if event.key == pygame.K_RIGHT and self.current_level.player.velocity.x > 0:
                    self.current_level.player.velocity.x = 0

    def update(self):
        self.current_level.update()
        # TODO: Punktestand und Spielzustand aktualisieren

    def draw(self):
        self.screen.fill((0, 0, 0))  # Hintergrund
        self.current_level.draw(self.screen)
        pygame.display.flip()

class Level:
    def __init__(self, number):
        self.number = number
        self.layout = None  # Level-Daten laden
        self.player = Player(100, 400, None)  # Platzhalter für Sprite
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.load()

    def load(self):
        # TODO: Layout, Gegner, PowerUps etc. basierend auf Level-Number laden
        # Temporäre Test-Plattformen hinzufügen
        self.platforms.add(Platform(0, HEIGHT - 50, WIDTH, 50))  # Boden
        self.platforms.add(Platform(200, HEIGHT - 150, 200, 20))  # Plattform 1
        self.platforms.add(Platform(500, HEIGHT - 250, 150, 20))  # Plattform 2

    def update(self):
        self.player.update(self.platforms)
        self.enemies.update()
        for enemy in self.enemies:
            if hasattr(enemy, 'update') and callable(enemy.update):
                enemy.update(self.platforms)  # Plattformen an Enemy.update() übergeben
        self.powerups.update()
        self.collectibles.update()
        self.platforms.update()

    def draw(self, screen):
        # TODO: Alle Sprites zeichnen
        self.platforms.draw(screen)
        self.collectibles.draw(screen)
        self.powerups.draw(screen)
        self.enemies.draw(screen)
        screen.blit(self.player.image, self.player.rect)

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((50, 50))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = pygame.math.Vector2(0, 0)
        self.health = 100
        self.on_ground = False  # Variable für Bodenkontakt

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def jump(self):
        # Nur springen, wenn der Charakter auf dem Boden ist
        if self.on_ground:
            self.velocity.y = -15  # Sprunggeschwindigkeit
            self.on_ground = False

    def update(self, platforms=None):
        # Schwerkraft anwenden
        self.velocity.y += GRAVITY
        
        # Maximale Fallgeschwindigkeit begrenzen
        if self.velocity.y > 15:
            self.velocity.y = 15
        
        # Horizontale Bewegung
        self.rect.x += self.velocity.x
        
        # Horizontale Kollisionsprüfung mit Plattformen
        if platforms:
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.velocity.x > 0:  # Bewegung nach rechts
                        self.rect.right = platform.rect.left
                    elif self.velocity.x < 0:  # Bewegung nach links
                        self.rect.left = platform.rect.right
        
        # Bildschirmgrenzen horizontal prüfen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
        
        # Vertikale Bewegung
        self.rect.y += self.velocity.y
        
        # Vertikale Kollisionsprüfung mit Plattformen
        self.on_ground = False
        if platforms:
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.velocity.y > 0:  # Charakter fällt nach unten
                        self.rect.bottom = platform.rect.top
                        self.velocity.y = 0
                        self.on_ground = True
                    elif self.velocity.y < 0:  # Charakter springt nach oben
                        self.rect.top = platform.rect.bottom
                        self.velocity.y = 0
        
        # Bildschirmgrenzen vertikal prüfen
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity.y = 0
        elif self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity.y = 0
            self.on_ground = True

class Player(Character):
    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)
        self.lives = 3
        self.weapon = Weapon(self)
        self.is_invincible = False

    def shoot(self):
        # TODO: Blase abfeuern
        pass

    def collect(self, item):
        # TODO: Sammeln
        pass

    def take_damage(self, amount):
        if not self.is_invincible:
            self.health -= amount
            if self.health <= 0:
                self.lives -= 1
                # TODO: Leben verloren verarbeiten

    def update(self, platforms=None):
        super().update(platforms)
        # Kollisionen mit Plattformen prüfen (wird vom Level aufgerufen)
        # TODO: Spieler-Eingabe, Zustand prüfen

class Enemy(Character):
    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)
        self.speed = 2
        self.state = '''idle'''

    def attack(self):
        # TODO: Angriffsverhalten
        pass

    def update(self, platforms):
        super().update(platforms)
        # TODO: KI-Verhalten

class Weapon:
    def __init__(self, owner):
        self.owner = owner
        self.cooldown = 0

    def fire(self):
        # TODO: Projektil erzeugen
        pass

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((10, 10))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = pygame.math.Vector2(0, -5)

    def update(self):
        self.rect.move_ip(self.velocity)
        # TODO: Bildschirmgrenzen prüfen

class Bubble(Projectile):
    def __init__(self, x, y, captured_enemy=None):
        super().__init__(x, y, None)
        self.captured_enemy = captured_enemy

    def rise(self):
        # TODO: Aufsteigen und Blase platzen
        pass

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
    
    #TODO: Plattform-Logik (Bewegung, Kollision)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((30, 30))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = random.choice(['health', 'ammo'])

class DoubleEspresso(PowerUp):
        def __init__(self, x, y):
            super().__init__(x, y, None)
            self.image.fill((255, 0, 0))
            self.type = 'double_espresso'

class CheatsheetScroll(PowerUp):
        def __init__(self, x, y):
            super().__init__(x, y, None)
            self.image.fill((0, 0, 255))
            self.type = 'cheatsheet_scroll'

class SemesterbreakAura(PowerUp):
        def __init__(self, x, y):
            super().__init__(x, y, None)
            self.image.fill((0, 255, 0))
            self.type = 'semesterbreak_aura'

class MotivationFishBread(PowerUp):
        def __init__(self, x, y):
            super().__init__(x, y, None)
            self.image.fill((255, 0, 255))
            self.type = 'motivation_fishbread'

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((20, 20))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = random.choice(['coin', 'gem'])

    def collect(self, player):
        pass

    def update(self):
        pass

class Creditpoint(Collectible):
        def __init__(self, x, y):
            super().__init__(x, y, None)
            self.image.fill((255, 215, 0))
            self.type = 'CP'

class Grade(Collectible):
        def __init__(self, x, y):
            super().__init__(x, y, None)
            self.image.fill((0, 0, 255))
            self.type = 'grade'


    
        

# TODO: Weitere Klassen: PowerUp, Collectible, Platform

if __name__ == "__main__":
    game = Game()
    game.start()