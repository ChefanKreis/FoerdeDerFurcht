import pygame
from settings import WIDTH, HEIGHT, GRAVITY, PLAYER_JUMP_STRENGTH, ENEMY_HEALTH, COLOR_WHITE, MAX_FALL_SPEED

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((50, 50))
        # Nur mit weißer Farbe füllen, wenn kein Sprite vorhanden ist
        if sprite is None:
            self.image.fill(COLOR_WHITE)
        
        # Kollisionsbox exakt auf Sprite-Größe setzen
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = pygame.math.Vector2(0, 0)
        self.health = ENEMY_HEALTH
        self.on_ground = False  # Variable für Bodenkontakt
        
        # Level-Grenzen (werden vom Level gesetzt)
        self.level_width = WIDTH  # Standard-Wert, wird überschrieben
        self.level_height = HEIGHT

        #Betäubung durch Syntax Scream
        self.is_stunned = False
        self.stun_timer = 0
        self.stun_effect_color = (255, 0, 0, 70)  # Rot mit Transparenz


    def move(self, dx, dy):

        if not self.is_stunned:
            self.rect.x += dx
            self.rect.y += dy

    def jump(self):
        # Nur springen, wenn der Charakter auf dem Boden ist
        if self.on_ground and not self.is_stunned:
            self.velocity.y = PLAYER_JUMP_STRENGTH  # Sprunggeschwindigkeit
            self.on_ground = False

    def update(self, platforms=None):
        # Schwerkraft anwenden
        self.velocity.y += GRAVITY
        
        #Betäubungseffekt anwenden
        if self.is_stunned:
            self.velocity.x = 0  # Keine horizontale Bewegung während der Betäubung
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.is_stunned = False

        # Maximale Fallgeschwindigkeit begrenzen
        if self.velocity.y > MAX_FALL_SPEED:
            self.velocity.y = MAX_FALL_SPEED
        
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
        
        # Level-Grenzen horizontal prüfen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.level_width:
            self.rect.right = self.level_width
        
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
        
        # Level-Grenzen vertikal prüfen
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity.y = 0
        elif self.rect.bottom > self.level_height:
            self.rect.bottom = self.level_height
            self.velocity.y = 0
            self.on_ground = True

    def apply_stun(self, duration):
        """Wendet eine Betäubung an, die die Bewegung des Charakters für eine bestimmte Zeit stoppt."""
        self.is_stunned = True
        self.stun_timer = duration
        self.velocity.x = 0
        self.velocity.y = 0