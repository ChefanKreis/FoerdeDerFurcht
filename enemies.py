import pygame
import random
from settings import WIDTH, HEIGHT, GRAVITY, PLAYER_JUMP_STRENGTH, ENEMY_SPEED, ENEMY_HEALTH, COLOR_WHITE, COLOR_YELLOW, COLOR_BLUE, COLOR_BLACK
from character import Character
from movement_enemies import HorizontalMovement, RandomJump, ChasePlayer, CombinedHorizontalandJump

class Enemy(Character):
    def __init__(self, x, y, sprite,level_width):
        super().__init__(x, y, sprite)
        self.level_width = level_width
        self.speed = ENEMY_SPEED
        self.state = '''idle'''
        self.movement_strategy = None #Bewegungsstrategie zuweisen

    def attack(self):
        # TODO: Angriffsverhalten
        pass

    def update(self, platforms, player = None, camera = None):

        if self.movement_strategy:
            self.movement_strategy.move(self, platforms, player, camera)

        super().update(platforms)

        
        # TODO: KI-Verhalten

class MultipleChoiceEnemy(Enemy):
    # Standardgegner
    # Bewegen sich am Boden hin und her, manchmal mit einem kleinen, unvorhersehbaren Sprung („Zufallsprinzip!")
    # Leicht in Blasen zu fangen

    def __init__(self, x, y, sprite, level_width):
        super().__init__(x, y, sprite, level_width)
        self.image = sprite or pygame.Surface((50, 50))
        self.image.fill((255, 0, 0)) #ROT
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity.x = 0.75  # Geschwindigkeit Enemy
        self.on_ground = True  # Standardmäßig auf dem Boden

        self.movement_strategy = CombinedHorizontalandJump(
            HorizontalMovement(speed=self.speed, left_x_world=0, right_x_world=level_width),
            RandomJump(jump_strength=-8, jump_chance=0.01)
        )    
        #self.movement_strategy = HorizontalMovement(speed=self.speed)
    
    def update(self, platforms, player=None, camera=None):
        super().update(platforms, player, camera)

    '''def move(self):
        # Bildschirmgrenzen horizontal prüfen
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.velocity.x *= -1  # Richtung umkehren, Bildschirmgrenze rechts und links
'''

    def attack(self):
        pass  # Angriff von MCE

    

class PythonEnemy(Enemy):
    # Agiler. Können höher springen und sich etwas schneller bewegen. 
    # Könnten eventuell kurze "Einrückungsfehler"-Projektile verschießen. 
    # Die Schattenbildung zeigt den Ort der Landung an.

    def __init__(self, x, y, sprite, level_width):
        super().__init__(x, y, sprite, level_width)
        self.image = sprite or pygame.Surface((50, 50))
        self.image.fill((COLOR_YELLOW)) #GELB
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity.x = 1  # Geschwindigkeit Enemy
        self.on_ground = True  # Standardmäßig auf dem Boden
    
        self.movement_strategy = CombinedHorizontalandJump(
            HorizontalMovement(speed=self.speed, left_x_world=0, right_x_world=level_width),
            RandomJump(jump_strength=-15, jump_chance=0.1)
        )


    def attack(self):   
        pass #Angriff von PEE

class ProgrammingTaskEnemy(Enemy):
    # Langsamer, aber robuster. Benötigen eventuell zwei Blasentreffer zum Fangen oder müssen öfter angestoßen werden, um zu platzen. 
    # Können kleine, nervige "Syntax-Fehler"-Bugs spawnen, die den Spieler kurzzeitig stören (z. B. kurz festhalten).

    def __init__(self, x, y, sprite, level_width):
        super().__init__(x, y, sprite, level_width)
        self.image = sprite or pygame.Surface((50, 50))
        self.image.fill((COLOR_BLUE)) #BLAU
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity.x = 1  # Geschwindigkeit Enemy
        self.on_ground = True  # Standardmäßig auf dem Boden

        self.movement_strategy = HorizontalMovement(speed=self.speed, left_x_world=0, right_x_world=level_width)

    def attack(self):
        pass #Angriff von PTE 


class Boss(Enemy):
    def __init__(self, x, y, sprite, level_width):
        super().__init__(x, y, sprite,level_width)
        self.image = sprite or pygame.Surface((75, 75))
        self.image.fill((COLOR_BLACK)) #BLACK
        self.rect = self.image.get_rect(topleft=(x, y))
        self.movement_strategy = ChasePlayer(speed = self.speed *0.75)

    def update(self, platforms, player = None, camera = None):
        super().update(platforms, player, camera)
        
    def attack(self):
        return super().attack()