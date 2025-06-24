import pygame
from settings import COLOR_PLATFORM
import random
import math

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        
        # Erstelle zunächst immer eine sichtbare Fallback-Surface
        self.image = pygame.Surface((width, height))
        self.image.fill(COLOR_PLATFORM)
        print(f"Platform-Basis erstellt: {width}x{height} mit Farbe {COLOR_PLATFORM}")
        
        # Versuche platforms.png zu laden und zu kacheln (optional)
        try:
            platform_texture = pygame.image.load("images/platforms.png").convert_alpha()
            tex_w, tex_h = platform_texture.get_size()
            print(f"Platform-Sprite geladen: {tex_w}x{tex_h} Pixel")
            
            # Sprite verkleinern falls es zu groß ist (raus zoomen)
            max_tile_size = 64  # Maximale Kachelgröße
            if tex_w > max_tile_size or tex_h > max_tile_size:
                # Proportional verkleinern
                scale_factor = min(max_tile_size / tex_w, max_tile_size / tex_h)
                new_w = int(tex_w * scale_factor)
                new_h = int(tex_h * scale_factor)
                platform_texture = pygame.transform.scale(platform_texture, (new_w, new_h))
                print(f"Sprite verkleinert von {tex_w}x{tex_h} auf {new_w}x{new_h}")
            
            if platform_texture.get_width() <= 0 or platform_texture.get_height() <= 0:
                print(f"FEHLER: Platform-Sprite hat ungültige Größe")
                raise ValueError("Sprite-Größe ungültig")
            
            self.image = self._create_tiled_surface(platform_texture, width, height)
            print(f"Platform-Textur geladen und gekachelt: {width}x{height}")
        except (pygame.error, FileNotFoundError, ValueError) as e:
            print(f"Platform-Textur 'platforms.png' konnte nicht geladen werden: {e}")
            print(f"Verwende Fallback-Plattform mit Farbe {COLOR_PLATFORM}")
            # Fallback wird bereits oben erstellt
    
    def _create_tiled_surface(self, texture, target_width, target_height):
        """Erstellt eine gekachelte Surface aus der gegebenen Textur"""
        tex_width, tex_height = texture.get_size()
        print(f"Kachele Textur: {tex_width}x{tex_height} auf Zielgröße: {target_width}x{target_height}")
        
        # Neue Surface mit Zielgröße erstellen (ohne SRCALPHA für bessere Sichtbarkeit)
        tiled_surface = pygame.Surface((target_width, target_height))        
        tiled_surface = tiled_surface.convert()
        
        # Einfaches Loop-System: Textur nahtlos wiederholen
        for y in range(0, target_height, tex_height):
            for x in range(0, target_width, tex_width):
                # Berechne wie viel von der aktuellen Kachel sichtbar ist
                visible_width = min(tex_width, target_width - x)
                visible_height = min(tex_height, target_height - y)
                
                if visible_width > 0 and visible_height > 0:
                    # Erstelle Clip-Bereich falls die Kachel abgeschnitten wird
                    if visible_width == tex_width and visible_height == tex_height:
                        # Komplette Kachel
                        tiled_surface.blit(texture, (x, y))
                    else:
                        # Abgeschnittene Kachel
                        clip_area = pygame.Rect(0, 0, visible_width, visible_height)
                        tiled_surface.blit(texture, (x, y), clip_area)
        
        print(f"Loop-Kachelung abgeschlossen")
        return tiled_surface

class BreakingPlatform(Platform):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        
        # Zustandsvariablen
        self.state = "stable"  # "stable", "cracking", "broken", "regenerating"
        self.break_timer = 0
        self.regenerate_timer = 0
        self.shake_offset = 0
        self.shake_intensity = 0
        
        # Konstanten für Timing (in Frames bei 60 FPS)
        self.CRACK_TIME = 90  # 1.5 Sekunden bis zum Brechen
        self.REGENERATE_TIME = 300  # 5 Sekunden Regenerationszeit
        self.player_on_platform = False
        
        # Original-Image für Regeneration speichern
        self.original_image = self.image.copy()
        
        # Verschiedene visuelle Zustände erstellen
        self._create_cracked_image()
        
        # Originalposition für Shake-Effekt
        self.original_rect = self.rect.copy()
        
    def _create_cracked_image(self):
        """Erstellt das rissige Aussehen der Plattform"""
        self.cracked_image = self.original_image.copy()
        
        # Risse hinzufügen (schwarze Linien)
        crack_color = (50, 50, 50)  # Dunkelgrau für Risse
        width, height = self.cracked_image.get_size()
        
        # Horizontale Risse
        for i in range(3):
            y_pos = height // 4 + i * (height // 4)
            start_x = random.randint(0, width // 4)
            end_x = random.randint(3 * width // 4, width)
            pygame.draw.line(self.cracked_image, crack_color, 
                           (start_x, y_pos), (end_x, y_pos), 2)
        
        # Vertikale Risse
        for i in range(2):
            x_pos = width // 3 + i * (width // 3)
            start_y = random.randint(0, height // 3)
            end_y = random.randint(2 * height // 3, height)
            pygame.draw.line(self.cracked_image, crack_color,
                           (x_pos, start_y), (x_pos, end_y), 1)
    
    def check_player_collision(self, player):
        """Prüft ob der Spieler auf der Plattform steht"""
        # Spieler steht auf Plattform wenn:
        # 1. Horizontal überlappt
        # 2. Spieler ist knapp über der Plattform
        # 3. Spieler fällt nach unten (positive Y-Geschwindigkeit)
        
        horizontal_overlap = (player.rect.right > self.rect.left and 
                            player.rect.left < self.rect.right)
        
        vertical_close = (player.rect.bottom <= self.rect.top + 10 and 
                         player.rect.bottom >= self.rect.top - 5)
        
        falling_or_landing = player.velocity.y >= 0
        
        was_on_platform = self.player_on_platform
        self.player_on_platform = (horizontal_overlap and vertical_close and 
                                  falling_or_landing and self.state != "broken")
        
        # Trigger brechen wenn Spieler zum ersten Mal auf Plattform landet
        if self.player_on_platform and not was_on_platform and self.state == "stable":
            self.start_breaking()
    
    def start_breaking(self):
        """Startet den Brech-Prozess"""
        if self.state == "stable":
            self.state = "cracking"
            self.break_timer = 0
            print(f"Plattform bei ({self.rect.x}, {self.rect.y}) beginnt zu brechen!")
    
    def update(self, player=None):
        """Aktualisiert den Zustand der brechenden Plattform"""
        try:
            if player:
                self.check_player_collision(player)
            
            if self.state == "cracking":
                self.break_timer += 1
                
                # Shake-Effekt während des Brechens
                self.shake_intensity = min(5, self.break_timer // 10)
                self.shake_offset = random.randint(-self.shake_intensity, self.shake_intensity)
                
                # Visueller Zustand ändern
                progress = self.break_timer / self.CRACK_TIME
                if progress < 0.5:
                    # Erste Hälfte: Original -> Gerissen
                    self.image = self._blend_images(self.original_image, self.cracked_image, progress * 2)
                else:
                    # Zweite Hälfte: Gerissen -> Transparenter
                    alpha = int(255 * (1 - ((progress - 0.5) * 2)))
                    self.image = self.cracked_image.copy()
                    self.image.set_alpha(alpha)
                
                # Brechen nach Timer
                if self.break_timer >= self.CRACK_TIME:
                    self.break_platform()
            
            elif self.state == "broken":
                self.regenerate_timer += 1
                if self.regenerate_timer >= self.REGENERATE_TIME:
                    self.regenerate_platform()
            
            elif self.state == "regenerating":
                # Regenerations-Animation
                progress = min(1.0, self.regenerate_timer / 30)  # 0.5 Sekunden Regeneration
                alpha = int(255 * progress)
                self.image = self.original_image.copy()
                self.image.set_alpha(alpha)
                
                self.regenerate_timer += 1
                if self.regenerate_timer >= 30:
                    self.state = "stable"
                    self.image = self.original_image.copy()
                    self.image.set_alpha(255)
                    print(f"Plattform bei ({self.rect.x}, {self.rect.y}) ist vollständig regeneriert!")
        except Exception as e:
            print(f"Fehler beim Update der brechenden Plattform bei ({self.rect.x}, {self.rect.y}): {e}")
            # Fallback: Stelle sicher, dass die Plattform einen gültigen Zustand hat
            if not hasattr(self, 'image') or self.image is None:
                self.image = self.original_image.copy()
            self.state = "stable"
    
    def _blend_images(self, img1, img2, factor):
        """Mischt zwei Bilder basierend auf einem Faktor (0.0 = img1, 1.0 = img2)"""
        result = img1.copy()
        alpha_surface = img2.copy()
        alpha_surface.set_alpha(int(255 * factor))
        result.blit(alpha_surface, (0, 0))
        return result
    
    def break_platform(self):
        """Lässt die Plattform brechen"""
        self.state = "broken"
        self.regenerate_timer = 0
        self.shake_offset = 0
        self.player_on_platform = False
        print(f"Plattform bei ({self.rect.x}, {self.rect.y}) ist gebrochen!")
        
        # Unsichtbar machen
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Komplett transparent
    
    def regenerate_platform(self):
        """Startet die Regeneration der Plattform"""
        self.state = "regenerating"
        self.regenerate_timer = 0
        print(f"Plattform bei ({self.rect.x}, {self.rect.y}) regeneriert sich!")
    
    def can_collide(self):
        """Gibt zurück ob die Plattform kollidierbar ist"""
        return self.state in ["stable", "cracking"]
    
    def get_render_rect(self):
        """Gibt das Rechteck für das Rendering zurück (mit Shake-Effekt)"""
        if self.state == "cracking" and self.shake_offset != 0:
            render_rect = self.rect.copy()
            render_rect.x += self.shake_offset
            return render_rect
        return self.rect
    