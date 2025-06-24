import pygame
from settings import COLOR_PLATFORM

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
    