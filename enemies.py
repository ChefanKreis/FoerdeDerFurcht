import pygame
import random
from settings import WIDTH, HEIGHT, GRAVITY, PLAYER_JUMP_STRENGTH, ENEMY_SPEED, ENEMY_HEALTH, COLOR_WHITE
from character import Character

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

    def move(self):
        # Bildschirmgrenzen horizontal prüfen
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.velocity.x *= -1  # Richtung umkehren, Bildschirmgrenze rechts und links

    def update(self, platforms):
        super().update(platforms)
        self.move()  # Bewegung update

    def attack(self):
        pass  # Angriff von MCE

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