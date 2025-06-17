"""
Kamera-System für das Spiel
Verwaltet die Ansicht und folgt dem Spieler durch das Level
"""

import pygame
from settings import WIDTH, HEIGHT

class Camera:
    def __init__(self, level_width, level_height):
        self.camera_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.level_width = level_width
        self.level_height = level_height
        self.x_offset = 0
        self.y_offset = 0
        
        # Kamera-Einstellungen
        self.follow_speed = 0.1  # Wie schnell die Kamera folgt (0.1 = smooth, 1.0 = sofort)
        self.x_deadzone = WIDTH // 3  # Bereich in der Mitte, wo sich der Spieler bewegen kann ohne Kamera-Bewegung
        self.y_deadzone = HEIGHT // 4
        
        # Grenzen für die Kamera
        self.x_min = 0
        self.x_max = level_width - WIDTH
        self.y_min = 0
        self.y_max = level_height - HEIGHT
    
    def update(self, target):
        """Aktualisiert die Kamera-Position basierend auf dem Ziel (normalerweise der Spieler)"""
        # Zielposition berechnen (Spieler zentriert)
        target_x = target.rect.centerx - WIDTH // 2
        target_y = target.rect.centery - HEIGHT // 2
        
        # Sanfte Kamera-Bewegung (Lerp)
        self.x_offset += (target_x - self.x_offset) * self.follow_speed
        self.y_offset += (target_y - self.y_offset) * self.follow_speed
        
        # Kamera in Level-Grenzen halten
        self.x_offset = max(self.x_min, min(self.x_offset, self.x_max))
        self.y_offset = max(self.y_min, min(self.y_offset, self.y_max))
        
        # Camera rect aktualisieren
        self.camera_rect.x = int(self.x_offset)
        self.camera_rect.y = int(self.y_offset)
    
    def apply(self, entity):
        """Wendet das Kamera-Offset auf eine Entity an und gibt die verschobene Position zurück"""
        return entity.rect.move(-self.camera_rect.x, -self.camera_rect.y)
    
    def apply_rect(self, rect):
        """Wendet das Kamera-Offset auf ein Rect an"""
        return rect.move(-self.camera_rect.x, -self.camera_rect.y)
    
    def update_with_deadzone(self, target):
        """Alternative Update-Methode mit Deadzone (Spieler kann sich in der Mitte bewegen ohne Kamera-Bewegung)"""
        # Horizontale Deadzone
        if target.rect.centerx - self.x_offset < self.x_deadzone:
            self.x_offset = target.rect.centerx - self.x_deadzone
        elif target.rect.centerx - self.x_offset > WIDTH - self.x_deadzone:
            self.x_offset = target.rect.centerx - WIDTH + self.x_deadzone
            
        # Vertikale Deadzone
        if target.rect.centery - self.y_offset < self.y_deadzone:
            self.y_offset = target.rect.centery - self.y_deadzone
        elif target.rect.centery - self.y_offset > HEIGHT - self.y_deadzone:
            self.y_offset = target.rect.centery - HEIGHT + self.y_deadzone
        
        # Kamera in Level-Grenzen halten
        self.x_offset = max(self.x_min, min(self.x_offset, self.x_max))
        self.y_offset = max(self.y_min, min(self.y_offset, self.y_max))
        
        # Camera rect aktualisieren
        self.camera_rect.x = int(self.x_offset)
        self.camera_rect.y = int(self.y_offset)
    
    def set_level_size(self, width, height):
        """Aktualisiert die Level-Größe für die Kamera-Grenzen"""
        self.level_width = width
        self.level_height = height
        self.x_max = max(0, width - WIDTH)
        self.y_max = max(0, height - HEIGHT) 