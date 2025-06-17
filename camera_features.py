"""
Erweiterte Kamera-Features für das Spiel
Parallax-Scrolling, Kamera-Zonen, Screen-Shake etc.
"""

import pygame
import math
from camera import Camera
from settings import WIDTH, HEIGHT

class AdvancedCamera(Camera):
    def __init__(self, level_width, level_height):
        super().__init__(level_width, level_height)
        
        # Screen Shake
        self.shake_amount = 0
        self.shake_timer = 0
        
        # Lookahead (Kamera schaut in Bewegungsrichtung voraus)
        self.lookahead_x = 0
        self.lookahead_amount = 100
        
    def shake(self, amount=10, duration=30):
        """Lässt den Bildschirm wackeln (z.B. bei Explosionen)"""
        self.shake_amount = amount
        self.shake_timer = duration
    
    def update_with_lookahead(self, target):
        """Kamera mit Vorausschau in Bewegungsrichtung"""
        # Lookahead basierend auf Spieler-Geschwindigkeit
        if hasattr(target, 'velocity'):
            self.lookahead_x = target.velocity.x * 10
            self.lookahead_x = max(-self.lookahead_amount, min(self.lookahead_x, self.lookahead_amount))
        
        # Zielposition mit Lookahead
        target_x = target.rect.centerx - WIDTH // 2 + self.lookahead_x
        target_y = target.rect.centery - HEIGHT // 2
        
        # Rest wie normale Update-Funktion
        self.x_offset += (target_x - self.x_offset) * self.follow_speed
        self.y_offset += (target_y - self.y_offset) * self.follow_speed
        
        # Screen Shake anwenden
        if self.shake_timer > 0:
            self.shake_timer -= 1
            shake_x = math.cos(self.shake_timer * 0.5) * self.shake_amount
            shake_y = math.sin(self.shake_timer * 0.7) * self.shake_amount
            self.x_offset += shake_x
            self.y_offset += shake_y
        
        # Kamera in Level-Grenzen halten
        self.x_offset = max(self.x_min, min(self.x_offset, self.x_max))
        self.y_offset = max(self.y_min, min(self.y_offset, self.y_max))
        
        self.camera_rect.x = int(self.x_offset)
        self.camera_rect.y = int(self.y_offset)


class ParallaxBackground:
    """Parallax-Hintergrund mit mehreren Ebenen"""
    
    def __init__(self):
        self.layers = []
        
    def add_layer(self, image_path, scroll_factor=0.5, y_offset=0):
        """Fügt eine Hintergrund-Ebene hinzu
        
        Args:
            image_path: Pfad zum Hintergrundbild
            scroll_factor: Wie schnell sich die Ebene bewegt (0.0 = statisch, 1.0 = mit Kamera)
            y_offset: Vertikaler Offset für die Ebene
        """
        try:
            image = pygame.image.load(image_path).convert()
            self.layers.append({
                'image': image,
                'scroll_factor': scroll_factor,
                'y_offset': y_offset,
                'width': image.get_width()
            })
        except pygame.error:
            print(f"Konnte Hintergrundbild nicht laden: {image_path}")
    
    def draw(self, screen, camera_x):
        """Zeichnet alle Parallax-Ebenen"""
        for layer in self.layers:
            # Berechne X-Position mit Parallax-Effekt
            x_offset = -camera_x * layer['scroll_factor']
            
            # Kacheln für endlosen Hintergrund
            x_position = x_offset % layer['width']
            
            # Zeichne zwei Kopien für nahtloses Scrolling
            screen.blit(layer['image'], (x_position - layer['width'], layer['y_offset']))
            screen.blit(layer['image'], (x_position, layer['y_offset']))
            if x_position < screen.get_width():
                screen.blit(layer['image'], (x_position + layer['width'], layer['y_offset']))


# Beispiel-Integration in Level-Klasse:
"""
class Level:
    def __init__(self, number):
        # ... andere Initialisierungen ...
        
        # Erweiterte Kamera
        self.camera = AdvancedCamera(self.level_width, self.level_height)
        
        # Parallax-Hintergrund
        self.parallax_bg = ParallaxBackground()
        self.parallax_bg.add_layer("images/bg_far.png", 0.3)    # Weit entfernt, bewegt sich langsam
        self.parallax_bg.add_layer("images/bg_mid.png", 0.6)    # Mittlere Distanz
        self.parallax_bg.add_layer("images/bg_near.png", 0.9)   # Nah, bewegt sich fast mit Kamera
    
    def update(self):
        # Kamera mit Lookahead aktualisieren
        self.camera.update_with_lookahead(self.player)
        
        # Bei besonderen Events Screen Shake auslösen
        # z.B. wenn ein großer Gegner besiegt wird:
        # self.camera.shake(amount=15, duration=45)
    
    def draw(self, screen):
        # Parallax-Hintergrund zuerst zeichnen
        self.parallax_bg.draw(screen, self.camera.x_offset)
        
        # Dann Rest des Levels mit Kamera-Offset
        # ... 
""" 