import pygame
import random


WIDTH, HEIGHT = 800, 600


class MovementStrategy:
# Basisklasse Bewegung Enemies

    def move(self, character, platforms):
        raise NotImplementedError("This method should be overridden by subclasses.")
    

class HorizontalMovement(MovementStrategy):
    def __init__(self, speed=2, left_x=0, right_x=WIDTH):
        self.left_x = left_x #Grenze links
        self.right_x = right_x #Grenze rechts
        self.speed = speed # Geshwindigkeit
        self.velocity = pygame.Vector2(speed, 0)
        

    def move(self, character, platforms):

        if not hasattr(character, 'velocity'):
            character.velocity = pygame.Vector2(self.speed, 0)

        if character.rect.left <= self.left_x:
           character.rect.left = self.left_x
           character.velocity.x *= -1

        elif character.rect.right == WIDTH:
            character.rect.right = WIDTH
            character.velocity.x *= -1
            

class RandomJump(MovementStrategy):
    def __init__(self, jump_strength=-5, jump_chance=0.5):
        self.jump_strength = jump_strength
        self.jump_chance = jump_chance

    
    def move(self, character, platforms):
        if character.on_ground:
            if random.random() < self.jump_chance:
                character.velocity.y = self.jump_strength
                character.on_ground = False
        # Implement random jump logic here


class ChasePlayer(MovementStrategy):
    def move(self, character, platforms):
        pass
        # Implement chase player logic here
