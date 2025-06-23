#########################################################################
# Import:     Alle Abhängigkeiten werden am Anfang eingebunden
#########################################################################

import pygame   # die Spiele-Engine
import random   # Zufallszahlen brauchen wir immer...
import os       # Das Dateisystem
import sys      # Systemfunktionen

# Importiere ausgelagerte Module
from settings import (WIDTH, HEIGHT, FPS, USE_SCALED, COLOR_HEART, COLOR_BACKGROUND)
from player import Player
from enemies import MultipleChoiceEnemy, PythonEnemy, ProgrammingTaskEnemy, Boss
from movement_enemies import MovementStrategy, HorizontalMovement, RandomJump, ChasePlayer
from weapons import Weapon, Bubble
from platforms import Platform
from powerups import *
from camera import Camera

# Konstanten werden jetzt aus settings.py importiert

#########################################################################
# Das Clock-Objekt:    Damit lassen sich Frames und Zeiten messen
#                      Sehr wichtig für Animationen etc.
#########################################################################

clock = pygame.time.Clock()

#########################################################################
# Screen wird jetzt in der Game-Klasse mit SCALED-Flag initialisiert
#########################################################################

# Das Dateisystem ermittelt das aktuelle Verzeichnis
game_folder = os.path.dirname(__file__)

#########################################################################
# Spezielle Klasse für den Hauptboden mit ground.png Textur
#########################################################################

class GroundPlatform(Platform):
    def __init__(self, x, y, width, height):
        # Zunächst normale Platform erstellen
        super().__init__(x, y, width, height)
        
        # Versucht ground.png zu laden
        try:
            ground_texture = pygame.image.load("images/ground.png").convert_alpha()
            tex_w, tex_h = ground_texture.get_size()
            
            # Neue Surface mit der Textur erstellen
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Textur über die gesamte Breite kacheln
            for ty in range(0, height, tex_h):
                for tx in range(0, width, tex_w):
                    self.image.blit(ground_texture, (tx, ty))
                    
        except (pygame.error, FileNotFoundError):
            # Fallback: Behalte die normale Platform-Darstellung
            pass

class Game:
    def __init__(self):
        pygame.init()
        # SCALED für Retro-Pixel-Effekt verwenden
        if USE_SCALED:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Klausur Chaos: Die Förde der Furcht")
        self.clock = pygame.time.Clock()
        self.running = True

        self.current_level = Level(1)
        self.score = 0
        self.game_over = False
        self.show_start_screen = True  # Startbildschirm anzeigen
        self.show_main_menu = True     # Hauptmenü anzeigen
        self.show_options = False      # Optionsmenü anzeigen
        
        # Font für Text-Darstellung
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.title_font = pygame.font.Font(None, 48)
        
        # Menü-Fonts (Serif-ähnlich, falls verfügbar)
        try:
            self.menu_font = pygame.font.Font("assets/fonts/serif.ttf", 32)
        except (pygame.error, FileNotFoundError):
            # Fallback auf System-Font
            self.menu_font = pygame.font.Font(None, 32)
        
        # Startbildschirm laden (falls vorhanden)
        self.start_screen_image = None
        # Verschiedene Bildformate versuchen
        image_files = ["startscreen.png", "startscreen.jpg", "startscreen.jpeg"]
        for image_file in image_files:
            try:
                self.start_screen_image = pygame.image.load(image_file)
                self.start_screen_image = pygame.transform.scale(self.start_screen_image, (WIDTH, HEIGHT))
                break
            except (pygame.error, FileNotFoundError):
                continue
        
        # Menü-Einstellungen (horizontale Animation von rechts)
        self.menu_animation_offset = 200  # Startet außerhalb des Bildschirms (nach rechts)
        self.menu_target_offset = 0       # Zielposition
        self.menu_animation_speed = 12    # Animationsgeschwindigkeit
        
        # Menü-Farben (warmes Gold)
        self.menu_accent_color = (210, 180, 140)  # Warmes Gold
        self.menu_hover_color = (255, 215, 0)     # Helleres Gold beim Hover
        self.menu_text_color = (255, 255, 255)    # Weißer Text
        
        # Button-Definitionen
        self.setup_menu_buttons()

        
      
        # Fallback wird automatisch in draw_start_screen() verwendet

    def start(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def setup_menu_buttons(self):
        """Erstellt die Menü-Buttons mit Positionen und Größen"""
        # Panel-Einstellungen (vertikal oben rechts)
        panel_width = 150
        panel_height = 180
        panel_x = WIDTH - panel_width - 30  # 30px Abstand vom rechten Rand
        panel_y = 50  # 50px Abstand vom oberen Rand
        
        # Button-Einstellungen (vertikal angeordnet)
        button_width = 120
        button_height = 40
        button_spacing = 15
        button_start_x = panel_x + (panel_width - button_width) // 2
        button_start_y = panel_y + 20  # 20px Abstand vom Panel-Rand
        
        # Button-Rectangles definieren (vertikal)
        self.menu_buttons = {
            "start": pygame.Rect(button_start_x, button_start_y, button_width, button_height),
            "options": pygame.Rect(button_start_x, button_start_y + button_height + button_spacing, button_width, button_height),
            "quit": pygame.Rect(button_start_x, button_start_y + 2 * (button_height + button_spacing), button_width, button_height)
        }
        
        # Panel-Rectangle
        self.menu_panel = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Button-Texte
        self.button_texts = {
            "start": "Start",
            "options": "Optionen", 
            "quit": "Beenden"
        }

    def draw_main_menu(self, screen, mouse_pos):
        """Zeichnet das stilvolle Hauptmenü über dem Startbildschirm"""
        # Startbildschirm als Hintergrund
        if self.start_screen_image:
            screen.blit(self.start_screen_image, (0, 0))
        else:
            # Fallback-Hintergrund
            screen.fill((20, 30, 50))
            title_text = self.big_font.render("FÖRDE DER FURCHT", True, (255, 215, 0))
            title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            screen.blit(title_text, title_rect)
        
        # Menü-Panel mit Animation (horizontal von rechts)
        animated_panel = self.menu_panel.copy()
        animated_panel.x += self.menu_animation_offset
        
        # Schatten-Effekt für das Panel
        shadow_offset = 4
        shadow_surface = pygame.Surface((animated_panel.width, animated_panel.height))
        shadow_surface.set_alpha(50)
        shadow_surface.fill((0, 0, 0))
        screen.blit(shadow_surface, (animated_panel.x + shadow_offset, animated_panel.y + shadow_offset))
        
        # Panel mit dunklem Hintergrund
        panel_surface = pygame.Surface((animated_panel.width, animated_panel.height))
        panel_surface.fill((25, 25, 30))  # Dunkles Grau wie im Optionsmenü
        
        # Goldener Rahmen um das Panel
        pygame.draw.rect(panel_surface, self.menu_accent_color, 
                        (0, 0, animated_panel.width, animated_panel.height), 3)
        
        screen.blit(panel_surface, (animated_panel.x, animated_panel.y))
        
        # Buttons zeichnen
        for button_name, button_rect in self.menu_buttons.items():
            # Button-Position mit Animation anpassen (horizontal)
            animated_button = button_rect.copy()
            animated_button.x += self.menu_animation_offset
            
            # Hover-Erkennung (mit animierter Position)
            is_hovered = animated_button.collidepoint(mouse_pos)
            
            # Button-Hintergrund (harmonischer mit dem Rest)
            button_color = (45, 45, 50) if not is_hovered else (60, 60, 65)
            pygame.draw.rect(screen, button_color, animated_button)
            
            # Button-Rahmen (dick bei Hover, dünn sonst)
            border_width = 3 if is_hovered else 2
            border_color = self.menu_hover_color if is_hovered else self.menu_accent_color
            pygame.draw.rect(screen, border_color, animated_button, border_width)
            
            # Subtiler Glow-Effekt bei Hover
            if is_hovered:
                # Innerer Glow
                inner_rect = animated_button.inflate(-6, -6)
                pygame.draw.rect(screen, (80, 80, 85), inner_rect, 1)
            
            # Button-Text mit kleinem Schatten-Effekt
            text_color = self.menu_hover_color if is_hovered else self.menu_text_color
            
            # Schatten-Text (subtil)
            shadow_surface = self.menu_font.render(self.button_texts[button_name], True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(animated_button.centerx + 1, animated_button.centery + 1))
            shadow_surface.set_alpha(100)
            screen.blit(shadow_surface, shadow_rect)
            
            # Haupttext
            text_surface = self.menu_font.render(self.button_texts[button_name], True, text_color)
            text_rect = text_surface.get_rect(center=animated_button.center)
            screen.blit(text_surface, text_rect)
        
        # Menü-Animation aktualisieren
        if self.menu_animation_offset > self.menu_target_offset:
            self.menu_animation_offset -= self.menu_animation_speed
            if self.menu_animation_offset < self.menu_target_offset:
                self.menu_animation_offset = self.menu_target_offset

    def handle_menu_events(self, event):
        """Behandelt Menü-Event-Handling"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Linke Maustaste
                mouse_pos = pygame.mouse.get_pos()
                
                # Prüfe jeden Button (mit Animation berücksichtigen)
                for button_name, button_rect in self.menu_buttons.items():
                    animated_button = button_rect.copy()
                    animated_button.x += self.menu_animation_offset
                    
                    if animated_button.collidepoint(mouse_pos):
                        if button_name == "start":
                            self.start_game()
                        elif button_name == "options":
                            self.open_settings()
                        elif button_name == "quit":
                            self.running = False
                        break

    def start_game(self):
        """Startet das Spiel"""
        self.show_start_screen = False
        self.show_main_menu = False
        # Menü-Animation zurücksetzen für nächstes Mal
        self.menu_animation_offset = 200

    def open_settings(self):
        """Öffnet das Optionsmenü"""
        self.show_options = True
        self.show_main_menu = False  # Hauptmenü ausblenden

    def draw_options_menu(self, screen, mouse_pos):
        """Zeichnet das Optionsmenü mit Steuerungsinformationen"""
        # Startbildschirm als Hintergrund
        if self.start_screen_image:
            screen.blit(self.start_screen_image, (0, 0))
        else:
            # Fallback-Hintergrund
            screen.fill((20, 30, 50))
            title_text = self.big_font.render("FÖRDE DER FURCHT", True, (255, 215, 0))
            title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            screen.blit(title_text, title_rect)
        
        # Großes Panel für Optionen
        panel_width = 500
        panel_height = 420  # Höhe erhöht, um Platz für den Button zu schaffen
        panel_x = (WIDTH - panel_width) // 2
        panel_y = (HEIGHT - panel_height) // 2
        
        # Schatten-Effekt
        shadow_offset = 6
        shadow_surface = pygame.Surface((panel_width, panel_height))
        shadow_surface.set_alpha(50)
        shadow_surface.fill((0, 0, 0))
        screen.blit(shadow_surface, (panel_x + shadow_offset, panel_y + shadow_offset))
        
        # Hauptpanel
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.fill((25, 25, 30))  # Dunkles Grau statt Schwarz
        
        # Goldener Rahmen um das Panel
        pygame.draw.rect(panel_surface, self.menu_accent_color, 
                        (0, 0, panel_width, panel_height), 3)
        
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Titel des Optionsmenüs
        options_title = self.title_font.render("STEUERUNG", True, self.menu_hover_color)
        title_rect = options_title.get_rect(center=(WIDTH//2, panel_y + 35))
        screen.blit(options_title, title_rect)
        
        # Dezente Trennlinie unter dem Titel
        line_y = panel_y + 60
        line_color = (100, 90, 80)  # Gedämpftere Farbe
        pygame.draw.line(screen, line_color, 
                        (panel_x + 80, line_y), (panel_x + panel_width - 80, line_y), 2)
        
        # Steuerungsinformationen mit harmonischen Farben
        controls_sections = [
            {
                "title": "BEWEGUNG",
                "color": self.menu_accent_color,  # Warmes Gold
                "items": ["Pfeiltasten - Bewegen/Springen"]
            },
            {
                "title": "AKTIONEN",
                "color": (200, 170, 130),  # Gedämpftes Gold
                "items": ["LEERTASTE - Blasen schießen", "ESC - Zurück zum Hauptmenü"]
            },
            {
                "title": "SPIELZIEL",
                "color": (180, 150, 110),  # Noch gedämpfteres Gold
                "items": ["Fange Gegner mit Blasen und sammle", "Credit Points und Noten (1,0)!"]
            }
        ]
        
        # Text rendern
        y_offset = panel_y + 85
        
        for section in controls_sections:
            # Kategorie-Titel
            category_font = pygame.font.Font(None, 28)
            category_surface = category_font.render(section["title"], True, section["color"])
            category_rect = category_surface.get_rect(centerx=WIDTH//2, y=y_offset)
            screen.blit(category_surface, category_rect)
            
            # Kleine Linie unter Kategorie
            pygame.draw.line(screen, section["color"], 
                           (category_rect.left, category_rect.bottom + 2),
                           (category_rect.right, category_rect.bottom + 2), 1)
            
            y_offset += 35
            
            # Detail-Items
            detail_font = pygame.font.Font(None, 24)
            for item in section["items"]:
                item_surface = detail_font.render(item, True, (200, 200, 200))
                item_rect = item_surface.get_rect(centerx=WIDTH//2, y=y_offset)
                screen.blit(item_surface, item_rect)
                
                y_offset += 25
            
            y_offset += 15  # Extra Abstand zwischen Sektionen
        
        # Zurück-Button (weiter unten positioniert)
        back_button_width = 120
        back_button_height = 35
        back_button_x = WIDTH//2 - back_button_width//2
        back_button_y = panel_y + panel_height - 55  # Mehr Abstand vom Rand
        
        self.back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
        
        # Button-Styling
        is_hovered = self.back_button_rect.collidepoint(mouse_pos)
        button_color = (45, 45, 50) if not is_hovered else (60, 60, 65)
        pygame.draw.rect(screen, button_color, self.back_button_rect)
        
        # Button-Rahmen
        border_width = 3 if is_hovered else 2
        border_color = self.menu_hover_color if is_hovered else self.menu_accent_color
        pygame.draw.rect(screen, border_color, self.back_button_rect, border_width)
        
        # Button-Text
        text_color = self.menu_hover_color if is_hovered else self.menu_text_color
        back_text = self.menu_font.render("Zurück", True, text_color)
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        screen.blit(back_text, back_text_rect)

    def handle_options_events(self, event):
        """Behandelt Events im Optionsmenü"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Linke Maustaste
                mouse_pos = pygame.mouse.get_pos()
                
                if hasattr(self, 'back_button_rect') and self.back_button_rect.collidepoint(mouse_pos):
                    # Zurück zum Hauptmenü
                    self.show_options = False
                    self.show_main_menu = True
                    self.menu_animation_offset = 200  # Animation zurücksetzen
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC: Zurück zum Hauptmenü
                self.show_options = False
                self.show_main_menu = True
                self.menu_animation_offset = 200  # Animation zurücksetzen

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.show_start_screen and self.show_main_menu:
                # Hauptmenü-Events
                self.handle_menu_events(event)
            elif self.show_start_screen and self.show_options:
                # Optionsmenü-Events
                self.handle_options_events(event)
            elif event.type == pygame.KEYDOWN:
                if self.show_start_screen:
                    # Startbildschirm: Beliebige Taste startet das Spiel (Fallback)
                    self.show_start_screen = False
                    self.show_main_menu = False
                elif self.game_over:
                    # Bei Game Over: Neustart mit 'R' Taste
                    if event.key == pygame.K_r:
                        self.restart_game()
                else:
                    # Normale Spielsteuerung
                    player_speed = self.current_level.player.get_movement_speed()
                    if event.key == pygame.K_LEFT:
                        self.current_level.player.velocity.x = -player_speed
                    if event.key == pygame.K_RIGHT:
                        self.current_level.player.velocity.x = player_speed
                    if event.key == pygame.K_UP:
                        self.current_level.player.jump()
                    if event.key == pygame.K_SPACE:
                        self.current_level.player.shoot(self.current_level.projectiles)
                    # Debug: Schaden nehmen mit 'X' Taste
                    if event.key == pygame.K_x:
                        self.current_level.player.take_damage()
                    # Debug: PowerUp spawnen mit 'U' Taste
                    if event.key == pygame.K_u:
                        self.current_level._spawn_powerup(
                            self.current_level.player.rect.centerx + 50,
                            self.current_level.player.rect.centery
                        )
                    # ESC-Taste: Zurück zum Hauptmenü
                    if event.key == pygame.K_ESCAPE:
                        self.show_start_screen = True
                        self.show_main_menu = True
                        self.menu_animation_offset = 200  # Animation zurücksetzen
            if event.type == pygame.KEYUP:
                if not self.game_over and not self.show_start_screen:
                    if event.key == pygame.K_LEFT and self.current_level.player.velocity.x < 0:
                        self.current_level.player.velocity.x = 0
                    if event.key == pygame.K_RIGHT and self.current_level.player.velocity.x > 0:
                        self.current_level.player.velocity.x = 0

    def update(self):
        if not self.game_over and not self.show_start_screen:
            self.current_level.update()
            # Score vom Spieler übernehmen
            self.score = self.current_level.player.score
            # Prüfen ob Spieler alle Leben verloren hat
            if self.current_level.player.lives <= 0:
                self.game_over = True

    def draw(self):
        self.screen.fill((0, 0, 0))  # Hintergrund
        
        if self.show_start_screen:
            if self.show_main_menu:
                # Hauptmenü mit Mausposition
                mouse_pos = pygame.mouse.get_pos()
                self.draw_main_menu(self.screen, mouse_pos)
            elif self.show_options:
                # Optionsmenü mit Mausposition
                mouse_pos = pygame.mouse.get_pos()
                self.draw_options_menu(self.screen, mouse_pos)
            else:
                self.draw_start_screen()
        elif not self.game_over:
            self.current_level.draw(self.screen)
            self.draw_hud()
        else:
            self.draw_game_over()
            
        pygame.display.flip()

    def draw_start_screen(self):
        if self.start_screen_image:
            # Nur das Bild anzeigen - kein Text
            self.screen.blit(self.start_screen_image, (0, 0))
            
        else:
            # Fallback ohne Bild
            self.screen.fill((20, 30, 50))
            
            title_text = self.big_font.render("FÖRDE DER FURCHT", True, (255, 215, 0))
            title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            self.screen.blit(title_text, title_rect)
            
            subtitle_text = self.title_font.render("Klausur Chaos", True, (255, 255, 255))
            subtitle_rect = subtitle_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            self.screen.blit(subtitle_text, subtitle_rect)
            
            instruction_text = self.font.render("Drücke eine beliebige Taste zum Starten", True, (255, 255, 255))
            instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 80))
            self.screen.blit(instruction_text, instruction_rect)

    def draw_hud(self):
        # Herzen für Leben zeichnen
        heart_size = 30
        heart_margin = 5
        for i in range(self.current_level.player.lives):
            heart_x = 10 + i * (heart_size + heart_margin)
            heart_y = 10
            self.draw_heart(heart_x, heart_y, heart_size)
        
        # Score anzeigen
        score_text = self.font.render(f"Score: {self.current_level.player.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 50))
        
        # Credit Points anzeigen
        cp_text = self.font.render(f"CP: {self.current_level.player.credit_points}", True, (255, 215, 0))
        self.screen.blit(cp_text, (10, 80))
        
        # Grades anzeigen
        if self.current_level.player.grades_collected > 0:
            grades_text = self.font.render(f"Noten 1,0: {self.current_level.player.grades_collected}", True, (0, 255, 0))
            self.screen.blit(grades_text, (10, 110))
        
        # Aktive PowerUps anzeigen
        powerup_status = self.current_level.player.get_powerup_status()
        for i, status in enumerate(powerup_status):
            powerup_text = self.font.render(status, True, (255, 255, 0))
            self.screen.blit(powerup_text, (WIDTH - 250, 10 + i * 30))

    def draw_heart(self, x, y, size):
        # Einfaches Herz mit pygame.draw zeichnen
        # Herz aus zwei Kreisen und einem Dreieck
        heart_color = COLOR_HEART
        
        # Zwei obere Kreise
        circle_radius = size // 4
        pygame.draw.circle(self.screen, heart_color, (x + circle_radius, y + circle_radius), circle_radius)
        pygame.draw.circle(self.screen, heart_color, (x + size - circle_radius, y + circle_radius), circle_radius)
        
        # Unterer Teil des Herzens (Rechteck + Dreieck)
        pygame.draw.rect(self.screen, heart_color, (x, y + circle_radius, size, circle_radius))
        
        # Dreieck für die Herzspitze
        points = [
            (x + size // 2, y + size - 2),  # Spitze unten
            (x, y + size // 2),             # Links
            (x + size, y + size // 2)       # Rechts
        ]
        pygame.draw.polygon(self.screen, heart_color, points)

    def draw_game_over(self):
        # Hintergrund abdunkeln
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # "Zwangsexmatrikulation" Text
        game_over_text = self.big_font.render("ZWANGSEXMATRIKULATION", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # Zusätzliche Informationen
        subtitle_text = self.font.render("Alle Fehlversuche aufgebraucht!", True, (255, 255, 255))
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Neustart-Anweisung
        restart_text = self.font.render("Drücke 'R' für Neustart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
        # Finaler Punktestand
        final_score_text = self.font.render(f"Endpunktestand: {self.score}", True, (255, 255, 0))
        final_score_rect = final_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
        self.screen.blit(final_score_text, final_score_rect)

    def restart_game(self):
        # Spiel zurücksetzen
        self.game_over = False
        self.score = 0
        self.current_level = Level(1)
        self.show_start_screen = True  # Zurück zum Hauptmenü
        self.show_main_menu = True
        self.menu_animation_offset = 200  # Animation zurücksetzen

class Level:
    def __init__(self, number):
        self.number = number
        self.layout = None  # Level-Daten laden

        # Level-Größe (größer als der Bildschirm für Scrolling)
        self.level_width = WIDTH * 3 # 3x so breit wie der Bildschirm
        self.level_height = HEIGHT
        
        # Kamera initialisieren
        self.camera = Camera(self.level_width, self.level_height)
        
        # Player-Sprites laden
        player_sprites = self._load_player_sprites()
        self.player = Player(100, 400, player_sprites)

        # Gegner-Sprites laden
        self.enemy_sprites = self._load_enemy_sprites()  # Gegner-Sprites laden
        
        # Level-Größe an den Player weitergeben
        self.player.level_width = self.level_width
        self.player.level_height = self.level_height

        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()  # Gruppe für Projektile/Blasen

        
        
        # Hintergrund-Farbe oder -Bild
        self.background_color = (20, 30, 50)  # Dunkelblau
        
        # Hintergrundbild für das Level laden (vereinfachtes Parallax-System)
        self.background_texture = None
        self.parallax_factor = 0.5  # Hintergrund bewegt sich halb so schnell wie die Kamera
        
        try:
            # Hintergrundbild laden
            original_bg = pygame.image.load("images/foerde_background.png").convert()
            
            # Hintergrundbild auf Bildschirmhöhe skalieren
            scale_factor = HEIGHT / original_bg.get_height()
            scaled_width = int(original_bg.get_width() * scale_factor)
            self.background_texture = pygame.transform.scale(original_bg, (scaled_width, HEIGHT))
            
            print(f"Hintergrundbild geladen: {scaled_width}x{HEIGHT}")
                     
        except (pygame.error, FileNotFoundError) as e:
            print(f"Hintergrundbild 'foerde_background.png' konnte nicht geladen werden: {e}")
            self.background_texture = None
        
        self.load()

    def _load_player_sprites(self):
        """Lädt alle Player-Sprites für Animationen"""
        sprites = {}
        
        # Sprite-Definitionen: (key, dateiname, fallback_dateinamen)
        sprite_definitions = {
            'idle': ['player.png', 'Player.png', 'player_idle.png'],
            'jump': ['player_jump.png', 'Player_jump.png', 'player_jumping.png'],
            'run': ['player_run.png', 'Player_run.png', 'player_running.png']
        }
        
        for sprite_key, filenames in sprite_definitions.items():
            sprite = None
            for filename in filenames:
                image_path = f"images/{filename}"
                try:
                    sprite = pygame.image.load(image_path).convert_alpha()
                    sprite = pygame.transform.scale(sprite, (50, 50))  # Spieler-Größe
                    print(f"Player-{sprite_key}-Sprite geladen: {image_path}")
                    break
                except (pygame.error, FileNotFoundError):
                    continue
            
            if sprite is None:
                print(f"Player-{sprite_key}-Sprite nicht gefunden, verwende Fallback")
                # Fallback: Weißes Rechteck
                sprite = pygame.Surface((50, 50))
                sprite.fill((255, 255, 255))
            
            sprites[sprite_key] = sprite
        
        return sprites
    
      #############Enemys generieren######################
    def _load_enemy_sprites(self):
        
        enemy_sprites = {}
        
        # Sprite-Definitionen: (key, dateiname, fallback_dateinamen)
        sprite_definitions = {
            'multiple_choice': ['enemy_multiple_choice.png', 'Enemy_multiple_choice.png'],
            'python': ['enemy_python.png', 'Enemy_python.png'],
            'programming_task': ['enemy_programming_task.png', 'Enemy_programming_task.png'],
            'boss': ['enemy_boss.png', 'Boss.png']
        }
        
        for sprite_key, filenames in sprite_definitions.items():
            sprite = None
            for filename in filenames:
                image_path = f"images/{filename}"
                try:
                    sprite = pygame.image.load(image_path).convert_alpha()
                    sprite = pygame.transform.scale(sprite, (50, 50))  # Gegner-Größe
                    print(f"{sprite_key.capitalize()}-Sprite geladen: {image_path}")
                    break
                except (pygame.error, FileNotFoundError):
                    continue
            
            if sprite is None:
                print(f"{sprite_key.capitalize()}-Sprite nicht gefunden, verwende Fallback")
                # Fallback: Weißes Rechteck
                sprite = pygame.Surface((50, 50))
                sprite.fill((255, 255, 255))
            
            enemy_sprites[sprite_key] = sprite
        
        return enemy_sprites

    def load(self):
        # Erweiterte Level-Generierung für Scrolling
        # Boden über die gesamte Level-Breite
        ground_height = 50
        self.platforms.add(GroundPlatform(0, HEIGHT - ground_height, self.level_width, ground_height))
        
        # Plattformen über das Level verteilt
        platform_data = [
            # (x, y, width, height)
            (200, HEIGHT - 150, 200, 20),
            (500, HEIGHT - 250, 150, 20),
            (750, HEIGHT - 200, 100, 20),
            (900, HEIGHT - 300, 200, 20),
            (1200, HEIGHT - 150, 150, 20),
            (1400, HEIGHT - 350, 100, 20),
            (1600, HEIGHT - 200, 200, 20),
            (1850, HEIGHT - 300, 150, 20),
            (2100, HEIGHT - 250, 200, 20),
            (2350, HEIGHT - 150, 150, 20),
        ]
        
        for x, y, width, height in platform_data:
            self.platforms.add(Platform(x, y, width, height))
        
        # Gegner über das Level verteilt
        enemy_positions = [
            (300, HEIGHT - 100),
            (600, HEIGHT - 300),
            (1000, HEIGHT - 350),
            (1300, HEIGHT - 100),
            (1700, HEIGHT - 250),
            (2000, HEIGHT - 100),
            (2200, HEIGHT - 300),
        ]
        
        for i, (x, y) in enumerate(enemy_positions):
            if i % 3 == 0:
                enemy = MultipleChoiceEnemy(x, y, self.enemy_sprites['multiple_choice'], self.level_width) # Pass level_width
            elif i % 3 == 1:
                enemy = PythonEnemy(x, y, self.enemy_sprites['python'], self.level_width) # Pass level_width
            else:
                enemy = ProgrammingTaskEnemy(x, y, self.enemy_sprites['programming_task'], self.level_width) # Pass level_width
            
            self.enemies.add(enemy)
                
        ######## Boss am Ende hinzufügen ########
        boss_x = self.level_width - 300  # Boss am rechten Ende des Levels
        boss_y = HEIGHT - 200  # Etwas höher als der Boden
        boss = Boss(boss_x, boss_y, self.enemy_sprites['boss'], self.level_width)  # Pass level_width
        self.enemies.add(boss)
            
            #self.enemies.add(enemy)
        
        # PowerUps und Collectibles über das Level verteilt
        self._spawn_level_items()

    def update(self):
        self.player.update(self.platforms)
        
        # Kamera dem Spieler folgen lassen
        self.camera.update(self.player)  # Oder: self.camera.update_with_deadzone(self.player)
        
        for enemy in self.enemies:
            enemy.update(self.platforms, self.player, self.camera) # Spieler, Kamera übergeben
            
        
        # Gegner-Updates (mit Einfrieren-Check)
        for enemy in self.enemies:
            if hasattr(enemy, 'update') and callable(enemy.update):
                # Gegner nur aktualisieren wenn sie nicht eingefroren sind
                if not self.player.are_enemies_frozen():
                    enemy.update(self.platforms)
                else:
                    # Gefrorene Gegner: Nur Schwerkraft, keine Bewegung
                    enemy.velocity.x = 0  # Horizontale Bewegung stoppen
                    enemy.rect.y += enemy.velocity.y  # Schwerkraft weiter anwenden
                    enemy.velocity.y += 0.8  # Gravity

            # Kollision Spieler mit diesem Gegner prüfen
            if self.player.rect.colliderect(enemy.rect):
                if not self.player.is_invincible:
                    self.player.take_damage()
        
        self.powerups.update()
        self.collectibles.update()
        self.platforms.update()
        
        # Jedes Projektil mit Kamera-Referenz updaten
        for projectile in self.projectiles:
            projectile.update(self.camera)
        
        # Erweiterte Bubble-Logik
        self._handle_bubble_mechanics()
        
        # Kollisionserkennung: Projektile mit Gegnern
        for projectile in self.projectiles:
            if isinstance(projectile, Bubble):
                if not projectile.captured_enemy and not projectile.is_popping:
                    for enemy in self.enemies:
                        if projectile.rect.colliderect(enemy.rect):
                            projectile.capture_enemy(enemy)
                            # Credit Points spawnen wenn Gegner gefangen wird
                            self._spawn_creditpoint(enemy.rect.centerx, enemy.rect.centery)
                            break
        
        # Sammel-Kollisionen
        self._handle_collection_collisions()
    
    def _handle_bubble_mechanics(self):
        """Behandelt erweiterte Bubble-Mechaniken"""
        bubbles = [p for p in self.projectiles if isinstance(p, Bubble)]
        
        for bubble in bubbles:
            # Automatische Aufstieg-Logik
            bubble.update_rising_logic()
        
        # Optimierte Bubble-zu-Bubble Kollisionen
        for i, bubble in enumerate(bubbles):
            if bubble.can_be_popped():
                # Nur mit nachfolgenden Blasen prüfen (vermeidet doppelte Prüfungen)
                for other_bubble in bubbles[i+1:]:
                    if (other_bubble.can_be_popped() and
                        bubble.rect.colliderect(other_bubble.rect)):
                        
                        # Beide Blasen platzen lassen
                        bubble.pop()
                        other_bubble.pop()
                        break
    
    def _handle_collection_collisions(self):
        """Behandelt Kollisionen zwischen Spieler und Sammelobjekten"""
        # PowerUp-Kollisionen (optimiert mit spritecollide)
        collected_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in collected_powerups:
            self.player.collect(powerup)
        
        # Collectible-Kollisionen (optimiert mit spritecollide)
        collected_items = pygame.sprite.spritecollide(self.player, self.collectibles, True)
        for collectible in collected_items:
            self.player.collect(collectible)
    
    def _spawn_creditpoint(self, x, y):
        """Spawnt einen Credit Point an der angegebenen Position"""
        from powerups import Creditpoint
        cp = Creditpoint(x, y)
        self.collectibles.add(cp)
    
    def _spawn_powerup(self, x, y, powerup_type=None):
        """Spawnt ein PowerUp an der angegebenen Position"""
        from powerups import DoubleEspresso, CheatsheetScroll, SemesterbreakAura, MotivationFishBread
        import random
        
        if powerup_type is None:
            # Zufälliges PowerUp auswählen
            powerup_classes = [DoubleEspresso, CheatsheetScroll, SemesterbreakAura, MotivationFishBread]
            powerup_class = random.choice(powerup_classes)
        else:
            powerup_map = {
                'double_espresso': DoubleEspresso,
                'cheatsheet_scroll': CheatsheetScroll,
                'semesterbreak_aura': SemesterbreakAura,
                'motivation_fishbread': MotivationFishBread
            }
            powerup_class = powerup_map.get(powerup_type, DoubleEspresso)
        
        powerup = powerup_class(x, y)
        self.powerups.add(powerup)
    
    def _spawn_level_items(self):
        """Spawnt PowerUps und Collectibles über das gesamte Level verteilt"""
        from powerups import (DoubleEspresso, CheatsheetScroll, SemesterbreakAura, 
                             MotivationFishBread, Creditpoint, Grade)
        
        # PowerUps an verschiedenen Positionen im Level
        powerup_positions = [
            (300, HEIGHT - 200, DoubleEspresso),
            (800, HEIGHT - 250, CheatsheetScroll),
            (1100, HEIGHT - 350, SemesterbreakAura),
            (1500, HEIGHT - 400, MotivationFishBread),
            (1900, HEIGHT - 350, DoubleEspresso),
            (2300, HEIGHT - 200, CheatsheetScroll),
        ]
        
        for x, y, powerup_class in powerup_positions:
            self.powerups.add(powerup_class(x, y))
        
        # Credit Points über das gesamte Level verteilt
        for i in range(20):
            x = 200 + i * 150  # Alle 150 Pixel ein Credit Point
            y = HEIGHT - 100
            # Einige in der Luft platzieren
            if i % 3 == 0:
                y = HEIGHT - 200
            self.collectibles.add(Creditpoint(x, y))
        
        # Versteckte Grades (1,0-Noten) an besonderen Orten
        grade_positions = [
            (400, HEIGHT - 180),
            (1000, HEIGHT - 400),
            (1800, HEIGHT - 350),
            (2400, HEIGHT - 200),
        ]
        
        for x, y in grade_positions:
            self.collectibles.add(Grade(x, y))

    def draw(self, screen):
        # Hintergrund zeichnen
        screen.fill(self.background_color)
        
        # Hintergrundbild mit vereinfachtem Parallax-Effekt zeichnen
        if self.background_texture:
            # Parallax-Offset berechnen (Hintergrund bewegt sich langsamer)
            parallax_offset = self.camera.camera_rect.x * self.parallax_factor
            
            # Hintergrundbreite
            bg_width = self.background_texture.get_width()
            
            # Wie viele Kopien des Hintergrunds brauchen wir?
            tiles_needed = (self.level_width // bg_width) + 2
            
            # Hintergrundbild mehrfach nebeneinander zeichnen
            for i in range(tiles_needed):
                bg_x = i * bg_width - parallax_offset
                
                # Nur zeichnen wenn es auf dem Bildschirm sichtbar ist
                if bg_x + bg_width >= 0 and bg_x <= WIDTH:
                    screen.blit(self.background_texture, (bg_x, 0))
        
        # Alle Sprites mit Kamera-Offset zeichnen
        # Plattformen
        for platform in self.platforms:
            screen.blit(platform.image, self.camera.apply(platform))
        
        # Collectibles
        for collectible in self.collectibles:
            screen.blit(collectible.image, self.camera.apply(collectible))
        
        # PowerUps
        for powerup in self.powerups:
            screen.blit(powerup.image, self.camera.apply(powerup))

        for enemy in self.enemies:
            screen.blit(enemy.image, self.camera.apply(enemy))
        
        # Gegner zeichnen (mit Einfrieren-Effekt)
        for enemy in self.enemies:
            enemy_pos = self.camera.apply(enemy)
            if self.player.are_enemies_frozen():
                # Gefrorene Gegner: Bläulicher Tint
                frozen_surface = enemy.image.copy()
                frozen_overlay = pygame.Surface(frozen_surface.get_size())
                frozen_overlay.fill((100, 150, 255))  # Blauer Tint
                frozen_overlay.set_alpha(100)
                frozen_surface.blit(frozen_overlay, (0, 0))
                screen.blit(frozen_surface, enemy_pos)
            else:
                screen.blit(enemy.image, enemy_pos)
        
        # Projektile
        for projectile in self.projectiles:
            screen.blit(projectile.image, self.camera.apply(projectile))
        
        # Spieler zeichnen (mit Effekten)
        self._draw_player_with_effects(screen)
    
    def _draw_player_with_effects(self, screen):
        """Zeichnet den Spieler mit allen aktiven visuellen Effekten"""
        player_pos = self.camera.apply(self.player)
        
        # PowerUp-Effekte: Umrandung statt Overlay
        outline_colors = []
        if self.player.is_speed_boosted:
            outline_colors.append((255, 255, 0))  # Gelb für Geschwindigkeit
        
        if self.player.has_semesterbreak_aura:
            outline_colors.append((0, 255, 0))  # Grün für Unverwundbarkeit
        
        # Zeichne Umrandungen falls PowerUps aktiv sind
        if outline_colors:
            self._draw_player_outline(screen, player_pos, outline_colors)
        
        # Unverwundbarkeits-Blinken
        if self.player.is_invincible:
            # Blinken: Nur jede 10 Frames zeichnen
            if (self.player.invincibility_timer // 5) % 2 == 0:
                screen.blit(self.player.image, player_pos)
        else:
            screen.blit(self.player.image, player_pos)
    
    def _draw_player_outline(self, screen, player_pos, colors):
        """Zeichnet eine leuchtende Umrandung um den Player"""
        player_image = self.player.image
        
        # Erstelle eine Maske aus dem Player-Sprite
        mask = pygame.mask.from_surface(player_image)
        
        # Für jede Farbe eine Umrandung zeichnen
        for i, color in enumerate(colors):
            # Offset für mehrere Umrandungen
            offset = i + 1
            
            # Zeichne Umrandung in alle 8 Richtungen
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    if dx == 0 and dy == 0:
                        continue  # Überspringe das Zentrum
                    
                    # Position für diese Umrandung
                    outline_pos = (player_pos[0] + dx, player_pos[1] + dy)
                    
                    # Erstelle eine farbige Version der Maske
                    outline_surface = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
                    outline_surface.set_alpha(120 - i * 20)  # Mehrere Umrandungen werden schwächer
                    
                    screen.blit(outline_surface, outline_pos)

# Alle Klassen wurden in separate Module ausgelagert:
# - Character, Player -> player.py
# - Enemy-Klassen -> enemies.py
# - Movement-Strategien -> movement_enemies.py  
# - Weapon, Projectile, Bubble -> weapons.py
# - Platform -> platforms.py
# - PowerUps, Collectibles -> powerups.py

if __name__ == "__main__":
    game = Game()
    game.start()