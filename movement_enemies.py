import pygame
import random
from settings import WIDTH, HEIGHT




class MovementStrategy:
# Basisklasse Bewegung Enemies

    def move(self, character, platforms, player = None, camera = None):
        raise NotImplementedError("This method should be overridden by subclasses.")
    

class HorizontalMovement(MovementStrategy):
    def __init__(self, speed=2, left_x_world=0, right_x_world=None): # left_x und right_x als Weltkoordinaten
        self.left_x_world = left_x_world
        self.right_x_world = right_x_world # Kann None sein, dann volle Breite des Levels oder des Kamera-Bereichs
        self.speed = speed
        # self.velocity wird direkt im Character-Objekt manipuliert

    def move(self, character, platforms, player=None, camera=None):
        if not hasattr(character, 'velocity'):
            character.velocity = pygame.Vector2(self.speed, 0)

        # Sicherstellen, dass der Charakter eine Horizontalgeschwindigkeit hat, wenn er sich bewegen soll
        # Dies verhindert, dass der Gegner stehen bleibt, falls velocity.x auf 0 gesetzt wird
        if character.velocity.x == 0:
            # Setze eine zufällige Anfangsrichtung, wenn der Gegner feststeckt
            character.velocity.x = self.speed if random.random() > 0.5 else -self.speed

        # Bestimme die rechte Grenze. Priorität: right_x_world (falls explizit gesetzt), dann character.level_width, dann WIDTH*3.
        effective_right_bound = character.level_width if hasattr(character, 'level_width') and character.level_width is not None else WIDTH * 3
        if self.right_x_world is not None:
            effective_right_bound = self.right_x_world

        # Horizontale Bewegung anwenden
        character.rect.x += character.velocity.x

        # Richtung umkehren, wenn Levelgrenzen erreicht werden
        if character.rect.left <= self.left_x_world:
            character.rect.left = self.left_x_world
            character.velocity.x = abs(character.velocity.x)  # Sicherstellen, dass Geschwindigkeit positiv ist
        elif character.rect.right >= effective_right_bound:
            character.rect.right = effective_right_bound
            character.velocity.x = -abs(character.velocity.x) # Sicherstellen, dass Geschwindigkeit negativ ist


    """
    def __init__(self, speed=2, left_x=0, right_x=WIDTH):
        self.left_x = left_x #Grenze links
        self.right_x = right_x #Grenze rechts
        self.speed = speed # Geshwindigkeit
        self.velocity = pygame.Vector2(speed, 0)
        

    def move(self, character, platforms, player = None):

        if not hasattr(character, 'velocity'):
            character.velocity = pygame.Vector2(self.speed, 0)

        if character.rect.left <= self.left_x:
           character.rect.left = self.left_x
           character.velocity.x *= -1

        elif character.rect.right == WIDTH:
            character.rect.right = WIDTH
            character.velocity.x *= -1
      """      

class RandomJump(MovementStrategy):
    def __init__(self, jump_strength=-5, jump_chance=0.5):
        self.jump_strength = jump_strength
        self.jump_chance = jump_chance

    
    def move(self, character, platforms, player = None, camera = None):
        if character.on_ground:
            if random.random() < self.jump_chance:
                character.velocity.y = self.jump_strength
                character.on_ground = False
        # Implement random jump logic here

class CombinedHorizontalandJump(MovementStrategy):
    def __init__(self, *strategies):
        self.strategies = strategies

    def move(self, character, platforms, player=None, camera=None):
        # Geht alle Strategien durch und ruft deren move-Methode auf
        for strategy in self.strategies:
            strategy.move(character, platforms, player, camera)

class ChasePlayer(MovementStrategy):
    def __init__(self, speed=2):
        self.speed = speed

    def move(self, character, platforms, player, camera=None):
        if player:
            if character.rect.x < player.rect.x:
                character.velocity.x = self.speed
            elif character.rect.x > player.rect.x:
                character.velocity.x = -self.speed
            else:
                character.velocity.x = 0
        else:
            character.velocity.x = 0
        # Implement chase player logic here
