import pygame
import random
from settings import WIDTH, HEIGHT, GRAVITY, PLAYER_JUMP_STRENGTH, ENEMY_SPEED, ENEMY_HEALTH, COLOR_WHITE, COLOR_YELLOW, COLOR_BLUE, COLOR_BLACK
from settings import BOSS_ATTACK_COOLDOWN_SYNTAXSCREAM, BOSS_HEALTH, PLAYER_SCREAM_DURATION, BOSS_SCREAM_RADIUS, BOSS_SHOOTING_RADIUS # Boss related settings
from character import Character
from weapons import RedPen
from movement_enemies import HorizontalMovement, RandomJump, ChasePlayer, CombinedHorizontalandJump

class Enemy(Character):
    def __init__(self, x, y, sprite,level_width):
        super().__init__(x, y, sprite)
        self.level_width = level_width
        self.speed = ENEMY_SPEED
        self.state = '''idle'''
        self.movement_strategy = None #Bewegungsstrategie zuweisen

        self.base_image = sprite.copy() if sprite else pygame.Surface((50, 50))
        if sprite is None:
            self.base_image.fill(COLOR_WHITE)

        self.image = self.base_image

        if not hasattr(self, 'direction'):
            self.direction = 1    


    def attack(self):
        # TODO: Angriffsverhalten
        pass

    def update(self, platforms, player = None, camera = None):

        if self.movement_strategy:
            self.movement_strategy.move(self, platforms, player, camera)

        # Bild spiegeln
        if self.velocity.x > 0:  # Bewegung rechts
            self.image = self.base_image  # Originalbild nach rechts
        elif self.velocity.x < 0:  # Bewegung links
            self.image = pygame.transform.flip(self.base_image, True, False)  # Spiegle das Bild
        

        super().update(platforms)

        
        # TODO: KI-Verhalten

class MultipleChoiceEnemy(Enemy):
    # Standardgegner
    # Bewegen sich am Boden hin und her, manchmal mit einem kleinen, unvorhersehbaren Sprung („Zufallsprinzip!")
    # Leicht in Blasen zu fangen

    def __init__(self, x, y, sprite, level_width):
        super().__init__(x, y, sprite, level_width)

        self.movement_strategy = CombinedHorizontalandJump(
            HorizontalMovement(speed=self.speed, left_x_world=0, right_x_world=level_width),
            RandomJump(jump_strength=-8, jump_chance=0.01))    
        #self.movement_strategy = HorizontalMovement(speed=self.speed)
    
    def update(self, platforms, player=None, camera=None):
        super().update(platforms, player, camera)


    def attack(self):
        pass  # Angriff von MCE

    

class PythonEnemy(Enemy):
    # Agiler. Können höher springen und sich etwas schneller bewegen. 
    # Könnten eventuell kurze "Einrückungsfehler"-Projektile verschießen. 
    # Die Schattenbildung zeigt den Ort der Landung an.

    def __init__(self, x, y, sprite, level_width):
        super().__init__(x, y, sprite, level_width)

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

        self.movement_strategy = HorizontalMovement(speed=self.speed, left_x_world=0, right_x_world=level_width)

    def attack(self):
        pass #Angriff von PTE 



class Boss(Enemy):
    def __init__(self, x, y, sprite, level_width):
        super().__init__(x, y, sprite, level_width)
        
        boss_size = (75, 75)
        self.image = pygame.transform.scale(self.base_image, boss_size)
        self.base_image = pygame.transform.scale(self.base_image, boss_size)
        
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)
        self.health = BOSS_HEALTH
        self.movement_strategy = ChasePlayer(speed=self.speed)

        # Cooldown für die Stift Durchgang
        self.pen_attack_cooldown_ms = 5000
        self.last_pen_attack_time = 0

        # Cooldown für den Syntax Schrei
        self.last_scream_time = 0
        
        #Pen Feuern
        self.pens_to_fire = 0  #wie viele stifte übrig
        self.time_between_pens_ms = 5000  #Pause 5s
        self.last_pen_fired_time = 0 # Zeitstempel des letzten Schusses

        #Unverwundbarkeit
        self.is_invincible = False
        self.invincibility_duration = 500 # Dauer in ms
        self.invincibility_end_time = 0 # Zeitstempel, wann die Unverwundbarkeit endet

    def update(self, platforms, player=None, camera=None):
        # Führt die grundlegende Logik aus (Bewegung, Schwerkraft)
        super().update(platforms, player, camera)

        if not player:
            return

        current_time = pygame.time.get_ticks()

        distance_to_player = abs(self.rect.centerx-player.rect.centerx)

        #feuern prüfen
        if (self.pens_to_fire == 0 and 
            current_time - self.last_pen_attack_time > self.pen_attack_cooldown_ms and
            distance_to_player <= BOSS_SHOOTING_RADIUS):
            self.pens_to_fire = 5  # Starte einen Durchgang mit 5 Schuss
            self.last_pen_attack_time = current_time

        #Wird grad gefeuert prüfen
        if self.pens_to_fire > 0:
            if current_time - self.last_pen_fired_time > self.time_between_pens_ms:
                if player and hasattr(self, 'projectiles'):
                    new_pen = RedPen(self.rect.centerx, self.rect.centery, player)
                    self.projectiles.add(new_pen)
                
                self.pens_to_fire -= 1
                self.last_pen_fired_time = current_time

        #Unverwundbarkeit aufheben
        if self.is_invincible and current_time > self.invincibility_end_time:
            self.is_invincible = False

    def take_damage(self, amount=1):
        if not self.is_invincible:
            self.health -= amount
            self.is_invincible = True
            # Berechne den Endzeitpunkt der Unverwundbarkeit
            self.invincibility_end_time = pygame.time.get_ticks() + self.invincibility_duration

            if self.health <= 0:
                self.kill()

    def scream(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_scream_time >= BOSS_ATTACK_COOLDOWN_SYNTAXSCREAM:
            player.apply_stun(PLAYER_SCREAM_DURATION)
            self.last_scream_time = current_time
            return True
        return False
    
    def perform_boss_attack(self, player):
        #Syntax Schrei in bestimmtem Radius
        distance = abs(self.rect.centerx - player.rect.centerx)
        if distance <= BOSS_SCREAM_RADIUS:
            self.scream(player)
    