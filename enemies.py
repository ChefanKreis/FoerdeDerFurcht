import pygame
import random
from settings import WIDTH, HEIGHT, GRAVITY, PLAYER_JUMP_STRENGTH, ENEMY_SPEED, ENEMY_HEALTH, COLOR_WHITE

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((50, 50))
        self.image.fill(COLOR_WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = pygame.math.Vector2(0, 0)
        self.health = ENEMY_HEALTH
        self.on_ground = False  # Variable für Bodenkontakt

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def jump(self):
        # Nur springen, wenn der Charakter auf dem Boden ist
        if self.on_ground:
            self.velocity.y = PLAYER_JUMP_STRENGTH  # Sprunggeschwindigkeit
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

class Enemy(Character):
    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)
        self.speed = ENEMY_SPEED
        self.state = '''idle'''

    def attack(self):
        # TODO: Angriffsverhalten
        pass

    def update(self, platforms):
        super().update(platforms)
        # TODO: KI-Verhalten

class MultipleChoiceEnemy(Enemy):
    # Standardgegner
    # Bewegen sich am Boden hin und her, manchmal mit einem kleinen, unvorhersehbaren Sprung („Zufallsprinzip!")
    # Leicht in Blasen zu fangen

    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)
        self.image = sprite or pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity.x = 1  # Geschwindigkeit Enemy
        self.on_ground = True  # Standardmäßig auf dem Boden
        self.direction = random.random() # Zufällige Richtung für den Start

    def move(self):
        # Bildschirmgrenzen vertikal prüfen
       if self.rect.left <= 0 or self.rect.right >= WIDTH:
           self.velocity.x *= -1  # Richtung umkehren, Bildschirmgrenze rechts und links

    #def random_jump(self):
           
    def update(self, platforms):
        super().update(platforms)
        self.move() # Bewegung update

    def attack(self):
        pass #Angriff von MCE

class PythonEnemy(Enemy):
    # Agiler. Können höher springen und sich etwas schneller bewegen. 
    # Könnten eventuell kurze "Einrückungsfehler"-Projektile verschießen. 
    # Die Schattenbildung zeigt den Ort der Landung an.

    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)

    def update(self, platforms):
        super().update(platforms)

    def attack(self):   
        pass #Angriff von PEE

class ProgrammingTaskEnemy(Enemy):
    # Langsamer, aber robuster. Benötigen eventuell zwei Blasentreffer zum Fangen oder müssen öfter angestoßen werden, um zu platzen. 
    # Können kleine, nervige "Syntax-Fehler"-Bugs spawnen, die den Spieler kurzzeitig stören (z. B. kurz festhalten).

    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)

    def update(self, platforms):
        super().update(platforms)

    def attack(self):
        pass #Angriff von PTE 