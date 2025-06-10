import pygame
from settings import WIDTH, HEIGHT, WEAPON_COOLDOWN, BUBBLE_SPEED, BUBBLE_LIFETIME, COLOR_BLUE, COLOR_BUBBLE

class Weapon:
    def __init__(self, owner):
        self.owner = owner
        self.cooldown = 0
        self.max_cooldown = WEAPON_COOLDOWN

    def fire(self, projectiles_group):
        if self.cooldown <= 0:
            # Richtung bestimmen (basierend auf der letzten Bewegung des Spielers)
            direction = 1  # Standard: nach rechts
            if self.owner.velocity.x < 0:
                direction = -1  # nach links
            elif self.owner.velocity.x == 0:
                direction = 1  # Standard: nach rechts wenn keine Bewegung
            
            # Neue Blase seitlich vom Spieler erzeugen
            bubble = Bubble(
                self.owner.rect.centerx + (direction * 30),  # 30 Pixel vor dem Spieler
                self.owner.rect.centery,  # Auf gleicher Höhe wie der Spieler
                direction  # Richtung an die Blase übergeben
            )
            projectiles_group.add(bubble)
            self.cooldown = self.max_cooldown
            return bubble
        return None
    
    def update(self):
        # Cooldown verringern
        if self.cooldown > 0:
            self.cooldown -= 1

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__()
        self.image = sprite or pygame.Surface((10, 10))
        self.image.fill(COLOR_BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = pygame.math.Vector2(0, -5)

    def update(self):
        self.rect.move_ip(self.velocity)
        # TODO: Bildschirmgrenzen prüfen

class Bubble(Projectile):
    def __init__(self, x, y, direction=1, captured_enemy=None):
        super().__init__(x, y, None)
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)  # Transparente Oberfläche
        pygame.draw.circle(self.image, COLOR_BUBBLE, (10, 10), 10, 2)  # Blaue Blase
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = pygame.math.Vector2(direction * BUBBLE_SPEED, 0)  # Horizontale Bewegung
        self.captured_enemy = captured_enemy
        self.lifetime = BUBBLE_LIFETIME
        
    def update(self):
        # Horizontal bewegen
        self.rect.x += self.velocity.x
        
        # Lebensdauer verringern
        self.lifetime -= 1
        
        # Blase entfernen wenn sie außerhalb des Bildschirms oder Lebensdauer abgelaufen
        if (self.lifetime <= 0 or 
            self.rect.right < 0 or 
            self.rect.left > WIDTH):
            self.kill()  # Blase entfernen
            if self.captured_enemy:
                self.release_enemy()
    
    def capture_enemy(self, enemy):
        if not self.captured_enemy:
            self.captured_enemy = enemy
            # Gegner unsichtbar machen (in der Blase gefangen)
            enemy.rect.center = self.rect.center
            enemy.velocity = pygame.math.Vector2(0, 0)  # Gegner kann sich nicht bewegen
            # Optional: Gegner aus enemies-Gruppe entfernen
            enemy.kill()
    
    def release_enemy(self):
        # Gegner wieder freigeben (falls implementiert)
        if self.captured_enemy:
            # Hier könnte man den Gegner wieder zur enemies-Gruppe hinzufügen
            # Oder ihn als "besiegt" markieren
            pass

    def rise(self):
        # TODO: Aufsteigen und Blase platzen
        pass 