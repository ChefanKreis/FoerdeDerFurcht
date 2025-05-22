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
ball = pygame.image.load(os.path.join(game_folder, 'ball.png')).convert_alpha()
imageRect = ball.get_rect()

#########################################################################
# Klassen: Spielfiguren, Gegner, PowerUps
#########################################################################

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
            # TODO: Eingaben (Bewegung, Schießen) hier abfragen

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
        pass

    def update(self):
        self.player.update()
        self.enemies.update()
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

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def jump(self):
        # TODO: Sprunglogik
        pass

    def update(self):
        # TODO: Gravitation, Kollisionen
        pass

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

    def update(self):
        super().update()
        # TODO: Spieler-Eingabe, Zustand prüfen

class Enemy(Character):
    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)
        self.speed = 2
        self.state = '''idle'''

    def attack(self):
        # TODO: Angriffsverhalten
        pass

    def update(self):
        super().update()
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

#########################################################################
# Game Loop:  Hier ist das Herzstück des Templates
# Im Game Loop laufen immer 5 Phasen ab:
# 1. Wait: Die Zeit zwischen 2 Frames wird mit Wartezeit gefüllt
# 2. Input: Alle (Input-)Events werden verarbeitet (Maus, Tastatur, etc.)
# 3. Update: Alle Sprites werden aktualisert inkl. Spiellogik
# 4. Render: Alle Sprites werden auf den Bildschirm gezeichnet
# 5. Double Buffering: Der Screen wird geswitcht und angezeigt
#########################################################################
running = True

while running:
    #########################################################################
    # 1. Wait-Phase:
    # Die pygame-interne Funktion clock.tick(FPS) berechnet die
    # tatsächliche Zeit zwischen zwei Frames und limitiert diese
    # auf einen Wert(z. B. 1/60). Diese tatsächliche verbrauchte
    # Zeit wird dann bei der Aktualisierung des Spiels benötigt,
    # um dieGeschwindigkeit der Objekte anzupassen.

    dt = clock.tick(FPS) / 1000

    #########################################################################
    # 2. Input-Phase:
    # Mit pygame.event.get() leeren wir den Event-Speicher.
    # Das ist wichtig, sonst läuft dieser voll und das Spiel stürzt ab.

    for event in pygame.event.get():
        if event.type == pygame.QUIT:   # Windows Close Button?
            running = False             # dann raus aus dem Game Loop

    #########################################################################
    # 3. Update-Phase: Hier ist die komplette Game Logik untergebracht.
    imageRect.topleft = (40,80)


    #########################################################################
    # 4. Render-Phase: Zeichne alles auf den Bildschirm

    # Hintergrund
    screen.fill((255, 255, 255))    # RGB Weiß

    # Zeichne Objekte an Position auf den Screen
    screen.blit(ball, imageRect)

    #########################################################################
    # 5. Double Buffering

    pygame.display.flip()

###########################
# Spiel verlassen: quit

pygame.quit()
