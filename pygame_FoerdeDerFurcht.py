#########################################################################
# Import:     Alle Abhängigkeiten werden am Anfang eingebunden
#########################################################################

import pygame   # die Spiele-Engine
import random   # Zufallszahlen brauchen wir immer...
import os       # Das Dateisystem
import sys      # Systemfunktionen

# Importiere ausgelagerte Module
from settings import (WIDTH, HEIGHT, FPS, USE_SCALED, COLOR_HEART, COLOR_BACKGROUND)
from settings import ANZAHL_ENEMYS_MAX, ANZAHL_ENEMYS_MIN,ENEMY_SPAWN_AREA_MIN, BOSS_HEALTH
from player import Player
from enemies import MultipleChoiceEnemy, PythonEnemy, ProgrammingTaskEnemy, Boss
from movement_enemies import MovementStrategy, HorizontalMovement, RandomJump, ChasePlayer
from weapons import Weapon, Bubble, RedPen
from platforms import Platform, BreakingPlatform
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
        self.level_complete = False    # Level-Sieg-Zustand
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
                elif self.level_complete:
                    # Bei Level Complete: Neustart mit 'R' oder Hauptmenü mit 'ESC'
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.show_start_screen = True
                        self.show_main_menu = True
                        self.level_complete = False
                        self.menu_animation_offset = 200  # Animation zurücksetzen
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
                        # Schießrichtung basierend auf aktuell gedrückten Richtungstasten bestimmen
                        keys = pygame.key.get_pressed()
                        shoot_direction = None
                        
                        if keys[pygame.K_LEFT]:
                            shoot_direction = -1  # Links schießen
                        elif keys[pygame.K_RIGHT]:
                            shoot_direction = 1   # Rechts schießen
                        # Wenn keine Richtungstaste gedrückt, wird aktuelle facing_direction verwendet
                        
                        self.current_level.player.shoot(self.current_level.projectiles, shoot_direction)
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
                if not self.game_over and not self.show_start_screen and not self.level_complete:
                    if event.key == pygame.K_LEFT and self.current_level.player.velocity.x < 0:
                        self.current_level.player.velocity.x = 0
                    if event.key == pygame.K_RIGHT and self.current_level.player.velocity.x > 0:
                        self.current_level.player.velocity.x = 0

    def update(self):
        if not self.game_over and not self.show_start_screen and not self.level_complete:
            self.current_level.update()
            # Score vom Spieler übernehmen
            self.score = self.current_level.player.score
            # Prüfen ob Spieler alle Leben verloren hat
            if self.current_level.player.lives <= 0:
                self.game_over = True
            
            # Prüfen ob Boss besiegt wurde
            boss_defeated = self._check_boss_defeated()
            if boss_defeated:
                self.level_complete = True
                print("Level abgeschlossen! Boss besiegt!")

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
        elif self.level_complete:
            # Level abgeschlossen - Siegesbildschirm anzeigen
            self.draw_level_complete()
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

        # Boss Lebensanzeige erstellen und anzeigen
        boss = None #testet ob es Boss gibt
        for enemy in self.current_level.enemies:
            if isinstance(enemy, Boss):
                boss = enemy
                break  # Schleife beenden, da es nur einen Boss gibt

        
        if boss:
            # Einstellungen für die Lebensleiste
            bar_width = 250
            bar_height = 15
            bar_x = (WIDTH - bar_width) // 2  # Zentriert am oberen Rand
            bar_y = 20

            # Berechne den prozentualen Anteil der verbleibenden Lebenspunkte
            health_percentage = boss.health / BOSS_HEALTH
            current_health_width = bar_width * health_percentage

            # Hintergrund der Lebensleiste (dunkelrot)
            background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(self.screen, (139, 0, 0), background_rect)

            # Vordergrund der Lebensleiste (hellrot)
            # schrumpfende Gesundheit
            if current_health_width > 0:
                health_rect = pygame.Rect(bar_x, bar_y, current_health_width, bar_height)
                pygame.draw.rect(self.screen, (255, 69, 0), health_rect)

            # Schwarzer Rahmen
            pygame.draw.rect(self.screen, (0, 0, 0), background_rect, 3)

            # Name des Bosses über der Leiste anzeigen
            boss_name_text = self.font.render("Prof. Dr. Krauss", True, (255, 255, 255))
            text_rect = boss_name_text.get_rect(center=(WIDTH // 2, bar_y + bar_height + 15))
            self.screen.blit(boss_name_text, text_rect)

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

    def _check_boss_defeated(self):
        """Prüft ob der Boss besiegt wurde (nicht mehr in der enemies-Gruppe)"""
        # Prüfe ob mindestens ein Boss im Level existiert hat
        if not hasattr(self.current_level, '_boss_spawned'):
            # Prüfe ob ein Boss im Level vorhanden war
            for enemy in self.current_level.enemies:
                if isinstance(enemy, Boss):
                    self.current_level._boss_spawned = True
                    break
            else:
                # Kein Boss im Level gefunden
                return False
        
        # Prüfe ob Boss noch vorhanden ist
        for enemy in self.current_level.enemies:
            if isinstance(enemy, Boss):
                return False  # Boss noch vorhanden
        
        # Boss wurde gespawnt aber ist nicht mehr da = besiegt
        return hasattr(self.current_level, '_boss_spawned') and self.current_level._boss_spawned
    
    def draw_level_complete(self):
        """Zeichnet den Level-Complete-Bildschirm"""
        # Hintergrund abdunkeln
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Goldener Hintergrund für den Siegestext
        victory_panel_width = 600
        victory_panel_height = 400
        panel_x = (WIDTH - victory_panel_width) // 2
        panel_y = (HEIGHT - victory_panel_height) // 2
        
        # Panel mit Gradient-Effekt
        panel_surface = pygame.Surface((victory_panel_width, victory_panel_height))
        panel_surface.fill((40, 40, 50))  # Dunkler Hintergrund
        
        # Goldener Rahmen
        pygame.draw.rect(panel_surface, (255, 215, 0), 
                        (0, 0, victory_panel_width, victory_panel_height), 5)
        
        # Innerer Glow-Effekt
        inner_rect = pygame.Rect(5, 5, victory_panel_width - 10, victory_panel_height - 10)
        pygame.draw.rect(panel_surface, (60, 60, 70), inner_rect, 2)
        
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Siegestext
        victory_title = self.big_font.render("PROFESSOR BESIEGT!", True, (255, 215, 0))
        title_rect = victory_title.get_rect(center=(WIDTH//2, panel_y + 70))
        self.screen.blit(victory_title, title_rect)
        
        # Untertitel
        subtitle = self.title_font.render("Klausur erfolgreich bestanden!", True, (0, 255, 0))
        subtitle_rect = subtitle.get_rect(center=(WIDTH//2, panel_y + 120))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Score-Informationen
        final_score = self.title_font.render(f"Endpunktestand: {self.score}", True, (255, 255, 255))
        score_rect = final_score.get_rect(center=(WIDTH//2, panel_y + 170))
        self.screen.blit(final_score, score_rect)
        
        # Credit Points
        final_cp = self.font.render(f"Credit Points gesammelt: {self.current_level.player.credit_points}", True, (255, 215, 0))
        cp_rect = final_cp.get_rect(center=(WIDTH//2, panel_y + 210))
        self.screen.blit(final_cp, cp_rect)
        
        # Grades
        final_grades = self.font.render(f"Noten 1,0 gesammelt: {self.current_level.player.grades_collected}", True, (0, 255, 0))
        grades_rect = final_grades.get_rect(center=(WIDTH//2, panel_y + 240))
        self.screen.blit(final_grades, grades_rect)
        
        # Überlebte Leben
        final_lives = self.font.render(f"Verbleibende Leben: {self.current_level.player.lives}", True, (255, 100, 100))
        lives_rect = final_lives.get_rect(center=(WIDTH//2, panel_y + 270))
        self.screen.blit(final_lives, lives_rect)
        
        # Trennlinie
        line_y = panel_y + 300
        pygame.draw.line(self.screen, (255, 215, 0), 
                        (panel_x + 50, line_y), (panel_x + victory_panel_width - 50, line_y), 2)
        
        # Anweisungen
        instruction1 = self.font.render("Drücke 'R' für Neustart", True, (255, 255, 255))
        instruction1_rect = instruction1.get_rect(center=(WIDTH//2, panel_y + 330))
        self.screen.blit(instruction1, instruction1_rect)
        
        instruction2 = self.font.render("Drücke 'ESC' für Hauptmenü", True, (255, 255, 255))
        instruction2_rect = instruction2.get_rect(center=(WIDTH//2, panel_y + 360))
        self.screen.blit(instruction2, instruction2_rect)

    def restart_game(self):
        # Spiel zurücksetzen
        self.game_over = False
        self.level_complete = False
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
        self.level_width = WIDTH * 16 # 16x so breit wie der Bildschirm für ein längeres Level
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
                    if sprite_key == 'boss':
                        # Boss größer skalieren, aber nicht zu groß
                        sprite = pygame.transform.scale(sprite, (80, 80))  # Boss-Größe
                    else:
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
        
        # Level in Zonen aufteilen (jede Zone = WIDTH Breite)
        # Zone 1-2: Tutorial/Einfach
        # Zone 3-4: Mittel
        # Zone 5-6: Schwer
        # Zone 7-8: Sehr schwer
        # Zone 9-10: Expert
        # Zone 11-12: Nightmare
        # Zone 13-14: Extreme
        # Zone 15-16: Final Boss
        
        # ZONE 1-2: TUTORIAL & EINFÜHRUNG (0 - WIDTH*2)
        # Garantiert erreichbare Plattformen (Max: 180 horizontal, 120 vertikal)
        tutorial_platforms = [
            (400, HEIGHT - 120, 200, 20),     # Erste Lernplattform
            (550, HEIGHT - 200, 150, 20),     # Erreichbar (150 horizontal, 80 vertikal)
            (750, HEIGHT - 140, 180, 20),     # Zurück nach unten (200 horizontal, 60 vertikal)
            (1000, HEIGHT - 180, 150, 20),    # Mittlere Höhe (250 horizontal, 40 vertikal)
            (1200, HEIGHT - 120, 200, 20),    # Leicht erreichbar (200 horizontal, 60 vertikal)
            (1450, HEIGHT - 200, 180, 20),    # Letzte Tutorial-Plattform (250 horizontal, 80 vertikal)
        ]
        
        # ZONE 3-4: MITTLERER BEREICH (WIDTH*2 - WIDTH*4)
        # Erreichbare Abstände mit progressiver Schwierigkeit
        medium_platforms = [
            (WIDTH*2 + 200, HEIGHT - 180, 120, 20),   # Zonenstart (einfacher Übergang)
            (WIDTH*2 + 370, HEIGHT - 260, 100, 20),   # Erreichbar (170 horizontal, 80 vertikal)
            (WIDTH*2 + 520, HEIGHT - 200, 80, 20),    # Abstieg (150 horizontal, 60 vertikal)
            (WIDTH*2 + 680, HEIGHT - 300, 80, 20),    # Hoch (160 horizontal, 100 vertikal)
            (WIDTH*2 + 840, HEIGHT - 220, 100, 20),   # Abstieg (160 horizontal, 80 vertikal)
            (WIDTH*3 + 20, HEIGHT - 280, 80, 20),     # Übergang neue Zone (180 horizontal, 60 vertikal)
            (WIDTH*3 + 180, HEIGHT - 200, 100, 20),   # Erreichbar (160 horizontal, 80 vertikal)
            (WIDTH*3 + 350, HEIGHT - 320, 80, 20),    # Hohe Plattform (170 horizontal, 120 vertikal)
            (WIDTH*3 + 500, HEIGHT - 240, 100, 20),   # Abstieg (150 horizontal, 80 vertikal)
        ]
        
        # ZONE 5-6: SCHWERER BEREICH (WIDTH*4 - WIDTH*6)
        # Maximale aber noch erreichbare Sprünge
        hard_platforms = [
            (WIDTH*4 + 150, HEIGHT - 200, 80, 20),    # Zonenstart
            (WIDTH*4 + 310, HEIGHT - 300, 60, 20),    # Erreichbar (160 horizontal, 100 vertikal)
            (WIDTH*4 + 450, HEIGHT - 220, 60, 20),    # Abstieg (140 horizontal, 80 vertikal)
            (WIDTH*4 + 600, HEIGHT - 340, 60, 20),    # Höchste Plattform (150 horizontal, 120 vertikal)
            (WIDTH*4 + 740, HEIGHT - 260, 80, 20),    # Abstieg (140 horizontal, 80 vertikal)
            (WIDTH*4 + 900, HEIGHT - 180, 80, 20),    # Niedrig (160 horizontal, 80 vertikal)
            (WIDTH*5 + 70, HEIGHT - 280, 60, 20),     # Hoch (170 horizontal, 100 vertikal)
            (WIDTH*5 + 210, HEIGHT - 200, 70, 20),    # Abstieg (140 horizontal, 80 vertikal)
            (WIDTH*5 + 360, HEIGHT - 320, 50, 20),    # Sehr hoch (150 horizontal, 120 vertikal)
            (WIDTH*5 + 490, HEIGHT - 240, 80, 20),    # Abstieg (130 horizontal, 80 vertikal)
            (WIDTH*5 + 650, HEIGHT - 180, 100, 20),   # Übergang Boss-Zone (160 horizontal, 60 vertikal)
        ]
        
        # ZONE 7-8: SEHR SCHWER (WIDTH*6 - WIDTH*8)
        very_hard_platforms = [
            (WIDTH*6 + 200, HEIGHT - 220, 80, 20),    # Übergang von schwer
            (WIDTH*6 + 350, HEIGHT - 300, 60, 20),    # Hoch (150 horizontal, 80 vertikal)
            (WIDTH*6 + 480, HEIGHT - 200, 60, 20),    # Abstieg (130 horizontal, 100 vertikal)
            (WIDTH*6 + 610, HEIGHT - 340, 50, 20),    # Sehr hoch (130 horizontal, 140 vertikal)
            (WIDTH*6 + 730, HEIGHT - 260, 60, 20),    # Abstieg (120 horizontal, 80 vertikal)
            (WIDTH*6 + 860, HEIGHT - 180, 70, 20),    # Niedrig (130 horizontal, 80 vertikal)
            (WIDTH*7 + 10, HEIGHT - 320, 50, 20),     # Übergang hoch (150 horizontal, 140 vertikal)
            (WIDTH*7 + 140, HEIGHT - 240, 60, 20),    # Abstieg (130 horizontal, 80 vertikal)
            (WIDTH*7 + 270, HEIGHT - 160, 80, 20),    # Niedrig (130 horizontal, 80 vertikal)
            (WIDTH*7 + 420, HEIGHT - 280, 60, 20),    # Hoch (150 horizontal, 120 vertikal)
            (WIDTH*7 + 550, HEIGHT - 200, 80, 20),    # Abstieg (130 horizontal, 80 vertikal)
        ]
        
        # ZONE 9-10: EXPERT (WIDTH*8 - WIDTH*10)
        expert_platforms = [
            (WIDTH*8 + 150, HEIGHT - 240, 60, 20),    # Expertenstart
            (WIDTH*8 + 270, HEIGHT - 320, 50, 20),    # Hoch (120 horizontal, 80 vertikal)
            (WIDTH*8 + 390, HEIGHT - 200, 50, 20),    # Abstieg (120 horizontal, 120 vertikal)
            (WIDTH*8 + 510, HEIGHT - 340, 40, 20),    # Sehr hoch (120 horizontal, 140 vertikal)
            (WIDTH*8 + 620, HEIGHT - 260, 50, 20),    # Abstieg (110 horizontal, 80 vertikal)
            (WIDTH*8 + 740, HEIGHT - 180, 60, 20),    # Niedrig (120 horizontal, 80 vertikal)
            (WIDTH*8 + 870, HEIGHT - 300, 50, 20),    # Hoch (130 horizontal, 120 vertikal)
            (WIDTH*9 + 20, HEIGHT - 220, 60, 20),     # Übergang (150 horizontal, 80 vertikal)
            (WIDTH*9 + 150, HEIGHT - 340, 40, 20),    # Sehr hoch (130 horizontal, 120 vertikal)
            (WIDTH*9 + 260, HEIGHT - 200, 50, 20),    # Abstieg (110 horizontal, 140 vertikal)
            (WIDTH*9 + 380, HEIGHT - 280, 50, 20),    # Hoch (120 horizontal, 80 vertikel)
            (WIDTH*9 + 500, HEIGHT - 160, 70, 20),    # Niedrig (120 horizontal, 120 vertikal)
            (WIDTH*9 + 630, HEIGHT - 240, 60, 20),    # Mittel (130 horizontal, 80 vertikal)
        ]
        
        # ZONE 11-12: NIGHTMARE (WIDTH*10 - WIDTH*12)
        nightmare_platforms = [
            (WIDTH*10 + 100, HEIGHT - 200, 50, 20),   # Nightmare Start
            (WIDTH*10 + 210, HEIGHT - 320, 40, 20),   # Hoch (110 horizontal, 120 vertikal)
            (WIDTH*10 + 310, HEIGHT - 240, 40, 20),   # Abstieg (100 horizontal, 80 vertikal)
            (WIDTH*10 + 410, HEIGHT - 360, 30, 20),   # Extrem hoch (100 horizontal, 120 vertikal)
            (WIDTH*10 + 500, HEIGHT - 280, 40, 20),   # Abstieg (90 horizontal, 80 vertikal)
            (WIDTH*10 + 600, HEIGHT - 200, 50, 20),   # Niedrig (100 horizontal, 80 vertikal)
            (WIDTH*10 + 720, HEIGHT - 340, 30, 20),   # Sehr hoch (120 horizontal, 140 vertikal)
            (WIDTH*10 + 810, HEIGHT - 260, 40, 20),   # Abstieg (90 horizontal, 80 vertikal)
            (WIDTH*10 + 920, HEIGHT - 180, 50, 20),   # Niedrig (110 horizontal, 80 vertikal)
            (WIDTH*11 + 50, HEIGHT - 300, 40, 20),    # Übergang hoch (130 horizontal, 120 vertikal)
            (WIDTH*11 + 160, HEIGHT - 220, 40, 20),   # Abstieg (110 horizontal, 80 vertikal)
            (WIDTH*11 + 270, HEIGHT - 340, 30, 20),   # Sehr hoch (110 horizontal, 120 vertikal)
            (WIDTH*11 + 360, HEIGHT - 260, 40, 20),   # Abstieg (90 horizontal, 80 vertikal)
            (WIDTH*11 + 470, HEIGHT - 180, 50, 20),   # Niedrig (110 horizontal, 80 vertikal)
            (WIDTH*11 + 590, HEIGHT - 280, 40, 20),   # Hoch (120 horizontal, 100 vertikal)
        ]
        
        # ZONE 13-14: EXTREME (WIDTH*12 - WIDTH*14)
        extreme_platforms = [
            (WIDTH*12 + 80, HEIGHT - 220, 40, 20),    # Extreme Start
            (WIDTH*12 + 180, HEIGHT - 340, 30, 20),   # Extrem hoch (100 horizontal, 120 vertikal)
            (WIDTH*12 + 270, HEIGHT - 260, 30, 20),   # Abstieg (90 horizontal, 80 vertikal)
            (WIDTH*12 + 360, HEIGHT - 180, 40, 20),   # Niedrig (90 horizontal, 80 vertikal)
            (WIDTH*12 + 470, HEIGHT - 320, 30, 20),   # Hoch (110 horizontal, 140 vertikal)
            (WIDTH*12 + 560, HEIGHT - 240, 30, 20),   # Abstieg (90 horizontal, 80 vertikal)
            (WIDTH*12 + 650, HEIGHT - 360, 25, 20),   # Extrem hoch (90 horizontal, 120 vertikal)
            (WIDTH*12 + 730, HEIGHT - 280, 30, 20),   # Abstieg (80 horizontal, 80 vertikal)
            (WIDTH*12 + 820, HEIGHT - 200, 40, 20),   # Niedrig (90 horizontal, 80 vertikal)
            (WIDTH*12 + 930, HEIGHT - 300, 30, 20),   # Hoch (110 horizontal, 100 vertikal)
            (WIDTH*13 + 40, HEIGHT - 220, 30, 20),    # Übergang (110 horizontal, 80 vertikal)
            (WIDTH*13 + 140, HEIGHT - 340, 25, 20),   # Extrem hoch (100 horizontal, 120 vertikal)
            (WIDTH*13 + 220, HEIGHT - 260, 30, 20),   # Abstieg (80 horizontal, 80 vertikal)
            (WIDTH*13 + 310, HEIGHT - 180, 40, 20),   # Niedrig (90 horizontal, 80 vertikal)
            (WIDTH*13 + 420, HEIGHT - 300, 30, 20),   # Hoch (110 horizontal, 120 vertikal)
            (WIDTH*13 + 520, HEIGHT - 240, 40, 20),   # Abstieg (100 horizontal, 60 vertikal)
        ]
        
        # ZONE 15-16: FINAL BOSS (WIDTH*14 - WIDTH*16)
        final_boss_platforms = [
            (WIDTH*14 + 200, HEIGHT - 220, 100, 20),  # Pre-Boss Plattform
            (WIDTH*14 + 350, HEIGHT - 300, 80, 20),   # Boss-Kampf hoch
            (WIDTH*14 + 500, HEIGHT - 180, 80, 20),   # Boss-Kampf niedrig
            (WIDTH*14 + 650, HEIGHT - 260, 80, 20),   # Boss-Kampf mittel
            (WIDTH*15 + 50, HEIGHT - 200, 120, 20),   # Boss-Arena Mitte
            (WIDTH*15 + 220, HEIGHT - 300, 100, 20),  # Boss-Arena hoch
            (WIDTH*15 + 370, HEIGHT - 220, 100, 20),  # Boss-Arena abstieg
            (WIDTH*15 + 520, HEIGHT - 340, 80, 20),   # Boss-Arena sehr hoch
            (WIDTH*15 + 650, HEIGHT - 160, 150, 20),  # Boss-Arena Ende
        ]
        
        # Alle Plattformen hinzufügen
        for platforms in [tutorial_platforms, medium_platforms, hard_platforms, very_hard_platforms, 
                         expert_platforms, nightmare_platforms, extreme_platforms, final_boss_platforms]:
            for x, y, width, height in platforms:
                self.platforms.add(Platform(x, y, width, height))
        
        # BRECHENDE PLATTFORMEN - strategisch ausgewählte Plattformen ersetzen
        breaking_platform_positions = [
            # Zone 1-2: Lerneffekt - ein paar brechende für Tutorial
            (550, HEIGHT - 200, 150, 20),     # Tutorial: Zweite Plattform
            (1200, HEIGHT - 120, 200, 20),    # Tutorial: Fünfte Plattform
            
            # Zone 3-4: Mittlerer Schwierigkeitsgrad
            (WIDTH*2 + 370, HEIGHT - 260, 100, 20),   # Mittlere Zone: Zweite Plattform
            (WIDTH*2 + 680, HEIGHT - 300, 80, 20),    # Mittlere Zone: Vierte Plattform
            (WIDTH*3 + 180, HEIGHT - 200, 100, 20),   # Mittlere Zone: Siebte Plattform
            
            # Zone 5-6: Schwieriger - mehr strategische Positionen
            (WIDTH*4 + 310, HEIGHT - 300, 60, 20),    # Schwer: Zweite Plattform
            (WIDTH*4 + 600, HEIGHT - 340, 60, 20),    # Schwer: Höchste Plattform (riskant!)
            (WIDTH*5 + 210, HEIGHT - 200, 70, 20),    # Schwer: Achte Plattform
            (WIDTH*5 + 490, HEIGHT - 240, 80, 20),    # Schwer: Zehnte Plattform
            
            # Zone 7-8: Sehr schwer - kritische Positionen
            (WIDTH*6 + 350, HEIGHT - 300, 60, 20),    # Sehr schwer: Zweite Plattform
            (WIDTH*6 + 610, HEIGHT - 340, 50, 20),    # Sehr schwer: Höchste Plattform
            (WIDTH*7 + 140, HEIGHT - 240, 60, 20),    # Sehr schwer: Achte Plattform
            
            # Zone 9-10: Expert - nur wenige, aber entscheidende
            (WIDTH*8 + 270, HEIGHT - 320, 50, 20),    # Expert: Zweite Plattform
            (WIDTH*8 + 510, HEIGHT - 340, 40, 20),    # Expert: Höchste Plattform
            (WIDTH*9 + 150, HEIGHT - 340, 40, 20),    # Expert: Sehr hohe Plattform
            
            # Zone 11-12: Nightmare - tückische Positionen
            (WIDTH*10 + 210, HEIGHT - 320, 40, 20),   # Nightmare: Zweite Plattform
            (WIDTH*10 + 410, HEIGHT - 360, 30, 20),   # Nightmare: Extrem hohe Plattform
            (WIDTH*11 + 270, HEIGHT - 340, 30, 20),   # Nightmare: Sehr hohe Plattform
            
            # Zone 13-14: Extreme - finale Herausforderung
            (WIDTH*12 + 180, HEIGHT - 340, 30, 20),   # Extreme: Extrem hohe Plattform
            (WIDTH*12 + 650, HEIGHT - 360, 25, 20),   # Extreme: Höchste Plattform
            (WIDTH*13 + 140, HEIGHT - 340, 25, 20),   # Extreme: Finale Herausforderung
        ]
        
        # Entferne die entsprechenden normalen Plattformen und ersetze sie durch brechende
        for x, y, width, height in breaking_platform_positions:
            # Finde und entferne die normale Plattform an dieser Position
            for platform in list(self.platforms):
                if (platform.rect.x == x and platform.rect.y == y and 
                    platform.rect.width == width and platform.rect.height == height):
                    self.platforms.remove(platform)
                    break
            
            # Füge die brechende Plattform hinzu
            breaking_platform = BreakingPlatform(x, y, width, height)
            self.platforms.add(breaking_platform)
            print(f"Brechende Plattform hinzugefügt bei ({x}, {y}) - {width}x{height}")
        
        # GEGNER-PLATZIERUNG (progressiv schwieriger)
        # Zone 1-2: Wenige, einfache Gegner
        easy_enemies = [
            (500, HEIGHT - 100, MultipleChoiceEnemy),
            (1200, HEIGHT - 100, MultipleChoiceEnemy),
            (1800, HEIGHT - 100, PythonEnemy),
        ]
        
        # Zone 3-4: Mehr Gegner, gemischte Typen
        medium_enemies = [
            (WIDTH*2 + 300, HEIGHT - 100, PythonEnemy),
            (WIDTH*2 + 600, HEIGHT - 250, MultipleChoiceEnemy),
            (WIDTH*2 + 900, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*3 + 200, HEIGHT - 350, PythonEnemy),
            (WIDTH*3 + 500, HEIGHT - 100, MultipleChoiceEnemy),
            (WIDTH*3 + 800, HEIGHT - 100, ProgrammingTaskEnemy),
        ]
        
        # Zone 5-6: Viele Gegner, schwierige Positionen
        hard_enemies = [
            (WIDTH*4 + 200, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*4 + 400, HEIGHT - 300, PythonEnemy),
            (WIDTH*4 + 600, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*4 + 800, HEIGHT - 250, MultipleChoiceEnemy),
            (WIDTH*5 + 150, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*5 + 350, HEIGHT - 330, PythonEnemy),
            (WIDTH*5 + 600, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*5 + 850, HEIGHT - 100, MultipleChoiceEnemy),
        ]
        
        # Zone 7-8: Sehr schwere Gegner
        very_hard_enemies = [
            (WIDTH*6 + 300, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*6 + 600, HEIGHT - 340, ProgrammingTaskEnemy),
            (WIDTH*6 + 900, HEIGHT - 100, PythonEnemy),
            (WIDTH*7 + 200, HEIGHT - 320, ProgrammingTaskEnemy),
            (WIDTH*7 + 500, HEIGHT - 100, ProgrammingTaskEnemy),
        ]
        
        # Zone 9-10: Expert Gegner
        expert_enemies = [
            (WIDTH*8 + 200, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*8 + 450, HEIGHT - 340, ProgrammingTaskEnemy),
            (WIDTH*8 + 700, HEIGHT - 100, PythonEnemy),
            (WIDTH*8 + 950, HEIGHT - 300, ProgrammingTaskEnemy),
            (WIDTH*9 + 200, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*9 + 450, HEIGHT - 340, PythonEnemy),
            (WIDTH*9 + 700, HEIGHT - 100, ProgrammingTaskEnemy),
        ]
        
        # Zone 11-12: Nightmare Gegner
        nightmare_enemies = [
            (WIDTH*10 + 150, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*10 + 350, HEIGHT - 360, ProgrammingTaskEnemy),
            (WIDTH*10 + 550, HEIGHT - 100, PythonEnemy),
            (WIDTH*10 + 750, HEIGHT - 340, ProgrammingTaskEnemy),
            (WIDTH*10 + 950, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*11 + 200, HEIGHT - 340, PythonEnemy),
            (WIDTH*11 + 400, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*11 + 650, HEIGHT - 280, ProgrammingTaskEnemy),
        ]
        
        # Zone 13-14: Extreme Gegner
        extreme_enemies = [
            (WIDTH*12 + 130, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*12 + 320, HEIGHT - 360, ProgrammingTaskEnemy),
            (WIDTH*12 + 520, HEIGHT - 100, PythonEnemy),
            (WIDTH*12 + 720, HEIGHT - 360, ProgrammingTaskEnemy),
            (WIDTH*12 + 920, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*13 + 150, HEIGHT - 340, PythonEnemy),
            (WIDTH*13 + 350, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*13 + 550, HEIGHT - 300, ProgrammingTaskEnemy),
        ]
        
        # Zone 15: Pre-Final-Boss Gegner
        prefinal_enemies = [
            (WIDTH*14 + 300, HEIGHT - 100, ProgrammingTaskEnemy),
            (WIDTH*14 + 600, HEIGHT - 300, ProgrammingTaskEnemy),
            (WIDTH*14 + 900, HEIGHT - 100, PythonEnemy),
            (WIDTH*15 + 200, HEIGHT - 340, ProgrammingTaskEnemy),
        ]
        
        # Gegner hinzufügen
        for enemy_group in [easy_enemies, medium_enemies, hard_enemies, very_hard_enemies,
                           expert_enemies, nightmare_enemies, extreme_enemies, prefinal_enemies]:
            for x, y, enemy_class in enemy_group:
                sprite_map = {
                    MultipleChoiceEnemy: 'multiple_choice',
                    PythonEnemy: 'python',
                    ProgrammingTaskEnemy: 'programming_task'
                }
                sprite_key = sprite_map.get(enemy_class, 'multiple_choice')
                enemy = enemy_class(x, y, self.enemy_sprites[sprite_key], self.level_width)
                self.enemies.add(enemy)

        # FINAL BOSS am Ende
        boss_x = self.level_width - 400  # Boss am rechten Ende des Levels
        boss_y = HEIGHT - 200  # Etwas höher als der Boden
        boss = Boss(boss_x, boss_y, self.enemy_sprites['boss'], self.level_width)
        self.enemies.add(boss)
        boss.projectiles = self.projectiles   
        
        # PowerUps und Collectibles über das Level verteilt
        self._spawn_level_items()

    def update(self):
        self.player.update(self.platforms)
        
        # Kamera dem Spieler folgen lassen
        self.camera.update(self.player)  # Oder: self.camera.update_with_deadzone(self.player)
        
        for enemy in self.enemies:
            if isinstance(enemy, Boss):
                enemy.perform_boss_attack(self.player) #Übergabe Projektile

            if not self.player.are_enemies_frozen():
                enemy.update(self.platforms, self.player, self.camera)

            else:
                # Update wenn eingefrorene Gegner 
                enemy.velocity.x = 0  # Horizontale Bewegung stoppen
                enemy.update(self.platforms) # Wende Schwerkraft und Kollision an
            
            # Kollision Spieler mit diesem Gegner prüfen
            if self.player.rect.colliderect(enemy.rect):
                if not self.player.is_invincible:
                    self.player.take_damage()          
         
            
            # Kollision Spieler mit diesem Gegner prüfen
            if self.player.rect.colliderect(enemy.rect):
                if not self.player.is_invincible:
                    self.player.take_damage()
        
        self.powerups.update()
        self.collectibles.update()
        
        # Plattformen updaten (brechende Plattformen brauchen Player-Referenz)
        for platform in self.platforms:
            if hasattr(platform, 'update') and hasattr(platform, 'check_player_collision'):
                # Brechende Plattform - braucht Player-Info
                platform.update(self.player)
            elif hasattr(platform, 'update'):
                # Normale Plattform
                platform.update()
        
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
                            if isinstance(enemy, Boss):
                                enemy.take_damage()
                                projectile.is_popping = True
                            else:

                                projectile.capture_enemy(enemy)
                                # Credit Points spawnen wenn Gegner gefangen wird
                                self._spawn_creditpoint(enemy.rect.centerx, enemy.rect.centery)
                            break
        #Kollisionserkennung Spieler Boss RedPen
        projectiles_hitting_player = pygame.sprite.spritecollide(self.player, self.projectiles, False)
        
        if projectiles_hitting_player:
            for projectile in projectiles_hitting_player:
                if isinstance(projectile, RedPen):
                    self.player.take_damage()
                    projectile.kill()
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
        
        # POWERUPS - Selten und abwechslungsreich platziert
        powerup_positions = [
            (1100, HEIGHT - 220, DoubleEspresso),               # Zone 1: Über vierter Plattform
            
            # Zone 3-4: Zwei PowerUps
            (WIDTH*2 + 730, HEIGHT - 340, CheatsheetScroll),    # Über vierter Plattform (hohe Plattform)
            (WIDTH*3 + 400, HEIGHT - 360, MotivationFishBread), # Über achter Plattform (hohe Plattform)
            
            # Zone 5-6: Drei PowerUps (schwerer zu erreichen)
            (WIDTH*4 + 360, HEIGHT - 340, SemesterbreakAura),   # Über zweiter Plattform (hoch)
            (WIDTH*4 + 650, HEIGHT - 380, DoubleEspresso),      # Über vierter Plattform (höchste)
            (WIDTH*5 + 410, HEIGHT - 360, CheatsheetScroll),    # Über neunter Plattform (sehr hoch)
            
            # Zone 7-8: Sehr schwer PowerUps
            (WIDTH*6 + 660, HEIGHT - 380, SemesterbreakAura),   # Über sehr hoher Plattform
            (WIDTH*7 + 470, HEIGHT - 320, MotivationFishBread), # Über hoher Plattform
            
            # Zone 9-10: Expert PowerUps
            (WIDTH*8 + 560, HEIGHT - 380, DoubleEspresso),      # Über sehr hoher Plattform
            (WIDTH*9 + 200, HEIGHT - 380, CheatsheetScroll),    # Über sehr hoher Plattform
            
            # Zone 11-12: Nightmare PowerUps
            (WIDTH*10 + 460, HEIGHT - 400, SemesterbreakAura),  # Über extrem hoher Plattform
            (WIDTH*11 + 320, HEIGHT - 380, MotivationFishBread), # Über sehr hoher Plattform
            
            # Zone 13-14: Extreme PowerUps
            (WIDTH*12 + 700, HEIGHT - 400, DoubleEspresso),     # Über extrem hoher Plattform
            (WIDTH*13 + 470, HEIGHT - 340, CheatsheetScroll),   # Über hoher Plattform
            
            # Zone 15: Pre-Final-Boss PowerUp
            (WIDTH*15 + 570, HEIGHT - 380, SemesterbreakAura),  # Über Boss-Arena sehr hoch
        ]
        
        for x, y, powerup_class in powerup_positions:
            self.powerups.add(powerup_class(x, y))
        
        # CREDIT POINTS - Abwechslungsreich verteilt (Boden, Luft, Plattformen)
        # Zone 1-2: Tutorial - gemischte Platzierung
        cp_positions_tutorial = [
            (500, HEIGHT - 160),   # Über erste Plattform (550, HEIGHT - 200)
            (650, HEIGHT - 100),   # Am Boden zwischen Plattformen
            (850, HEIGHT - 180),   # Über dritte Plattform (750, HEIGHT - 140)
            (1100, HEIGHT - 220),  # Über vierte Plattform (1000, HEIGHT - 180)
            (1300, HEIGHT - 160),  # Über fünfte Plattform (1200, HEIGHT - 120)
            (1550, HEIGHT - 240),  # Über sechste Plattform (1450, HEIGHT - 200)
            (1700, HEIGHT - 100),  # Am Boden am Ende
        ]
        
        # Zone 3-4: Mittlere Verteilung - mehr Abwechslung
        cp_positions_medium = [
            (WIDTH*2 + 100, HEIGHT - 100),   # Am Boden vor Zone
            (WIDTH*2 + 250, HEIGHT - 220),   # Über erste Plattform (WIDTH*2 + 200, HEIGHT - 180)
            (WIDTH*2 + 420, HEIGHT - 300),   # Über zweite Plattform (WIDTH*2 + 370, HEIGHT - 260)
            (WIDTH*2 + 570, HEIGHT - 240),   # Über dritte Plattform (WIDTH*2 + 520, HEIGHT - 200)
            (WIDTH*2 + 730, HEIGHT - 340),   # Über vierte Plattform (WIDTH*2 + 680, HEIGHT - 300)
            (WIDTH*2 + 890, HEIGHT - 260),   # Über fünfte Plattform (WIDTH*2 + 840, HEIGHT - 220)
            (WIDTH*2 + 950, HEIGHT - 100),   # Am Boden
            (WIDTH*3 + 70, HEIGHT - 320),    # Über sechste Plattform (WIDTH*3 + 20, HEIGHT - 280)
            (WIDTH*3 + 230, HEIGHT - 240),   # Über siebte Plattform (WIDTH*3 + 180, HEIGHT - 200)
            (WIDTH*3 + 400, HEIGHT - 360),   # Über achte Plattform (WIDTH*3 + 350, HEIGHT - 320)
            (WIDTH*3 + 550, HEIGHT - 280),   # Über neunte Plattform (WIDTH*3 + 500, HEIGHT - 240)
            (WIDTH*3 + 700, HEIGHT - 100),   # Am Boden am Ende
        ]
        
        # Zone 5-6: Spärliche Verteilung - herausfordernder
        cp_positions_hard = [
            (WIDTH*4 + 50, HEIGHT - 100),    # Am Boden vor Zone
            (WIDTH*4 + 250, HEIGHT - 320),   # Über erste Plattform
            (WIDTH*4 + 350, HEIGHT - 150),   # In der Luft (schwer erreichbar)
            (WIDTH*4 + 550, HEIGHT - 420),   # Über sehr hoher Plattform
            (WIDTH*4 + 700, HEIGHT - 100),   # Am Boden (große Lücke)
            (WIDTH*4 + 950, HEIGHT - 240),   # Über dritter Plattform
            (WIDTH*5 + 150, HEIGHT - 150),   # In der Luft
            (WIDTH*5 + 350, HEIGHT - 390),   # Über höchster Plattform
            (WIDTH*5 + 550, HEIGHT - 100),   # Am Boden
            (WIDTH*5 + 750, HEIGHT - 260),   # Über letzter Plattform
        ]
        
        # Zone 7-8: Sehr schwer - wenige, strategische CPs
        cp_positions_very_hard = [
            (WIDTH*6 + 150, HEIGHT - 100),   # Am Boden vor Zone
            (WIDTH*6 + 400, HEIGHT - 340),   # Über hoher Plattform
            (WIDTH*6 + 660, HEIGHT - 380),   # Über sehr hoher Plattform
            (WIDTH*6 + 910, HEIGHT - 220),   # Über niedrigerer Plattform
            (WIDTH*7 + 190, HEIGHT - 280),   # Über mittlerer Plattform
            (WIDTH*7 + 470, HEIGHT - 320),   # Über hoher Plattform
            (WIDTH*7 + 600, HEIGHT - 240),   # Über niedrigerer Plattform
        ]
        
        # Zone 9-10: Expert - spärliche Verteilung
        cp_positions_expert = [
            (WIDTH*8 + 100, HEIGHT - 100),   # Am Boden vor Zone
            (WIDTH*8 + 320, HEIGHT - 360),   # Über hoher Plattform
            (WIDTH*8 + 560, HEIGHT - 380),   # Über sehr hoher Plattform
            (WIDTH*8 + 790, HEIGHT - 220),   # Über niedrigerer Plattform
            (WIDTH*8 + 920, HEIGHT - 340),   # Über hoher Plattform
            (WIDTH*9 + 70, HEIGHT - 260),    # Über mittlerer Plattform
            (WIDTH*9 + 200, HEIGHT - 380),   # Über sehr hoher Plattform
            (WIDTH*9 + 430, HEIGHT - 320),   # Über hoher Plattform
            (WIDTH*9 + 550, HEIGHT - 200),   # Über niedrigerer Plattform
            (WIDTH*9 + 680, HEIGHT - 280),   # Über mittlerer Plattform
        ]
        
        # Zone 11-12: Nightmare - sehr spärlich
        cp_positions_nightmare = [
            (WIDTH*10 + 50, HEIGHT - 100),   # Am Boden vor Zone
            (WIDTH*10 + 260, HEIGHT - 360),  # Über hoher Plattform
            (WIDTH*10 + 460, HEIGHT - 400),  # Über extrem hoher Plattform
            (WIDTH*10 + 650, HEIGHT - 240),  # Über niedrigerer Plattform
            (WIDTH*10 + 860, HEIGHT - 380),  # Über sehr hoher Plattform
            (WIDTH*11 + 100, HEIGHT - 340),  # Über hoher Plattform
            (WIDTH*11 + 320, HEIGHT - 380),  # Über sehr hoher Plattform
            (WIDTH*11 + 520, HEIGHT - 220),  # Über niedrigerer Plattform
            (WIDTH*11 + 640, HEIGHT - 320),  # Über hoher Plattform
        ]
        
        # Zone 13-14: Extreme - minimal
        cp_positions_extreme = [
            (WIDTH*12 + 30, HEIGHT - 100),   # Am Boden vor Zone
            (WIDTH*12 + 230, HEIGHT - 380),  # Über extrem hoher Plattform
            (WIDTH*12 + 410, HEIGHT - 220),  # Über niedrigerer Plattform
            (WIDTH*12 + 570, HEIGHT - 280),  # Über mittlerer Plattform
            (WIDTH*12 + 700, HEIGHT - 400),  # Über extrem hoher Plattform
            (WIDTH*12 + 870, HEIGHT - 240),  # Über niedrigerer Plattform
            (WIDTH*13 + 90, HEIGHT - 260),   # Über mittlerer Plattform
            (WIDTH*13 + 190, HEIGHT - 380),  # Über extrem hoher Plattform
            (WIDTH*13 + 360, HEIGHT - 220),  # Über niedrigerer Plattform
            (WIDTH*13 + 470, HEIGHT - 340),  # Über hoher Plattform
        ]
        
        # Zone 15-16: Final Boss - strategische CPs
        cp_positions_final_boss = [
            (WIDTH*14 + 150, HEIGHT - 100),  # Am Boden vor Final Boss-Zone
            (WIDTH*14 + 400, HEIGHT - 340),  # Über hoher Plattform
            (WIDTH*14 + 700, HEIGHT - 300),  # Über mittlerer Plattform
            (WIDTH*15 + 100, HEIGHT - 240),  # Über Boss-Arena Plattform
            (WIDTH*15 + 320, HEIGHT - 340),  # Über hoher Boss-Arena Plattform
            (WIDTH*15 + 570, HEIGHT - 380),  # Über sehr hoher Boss-Arena Plattform
            (WIDTH*15 + 800, HEIGHT - 200),  # Über Boss-Arena Ende
        ]
        
        # Alle Credit Points hinzufügen
        for positions in [cp_positions_tutorial, cp_positions_medium, cp_positions_hard, cp_positions_very_hard,
                         cp_positions_expert, cp_positions_nightmare, cp_positions_extreme, cp_positions_final_boss]:
            for x, y in positions:
                self.collectibles.add(Creditpoint(x, y))
        
        # GRADES (1,0-NOTEN) - Sehr selten und schwer erreichbar (verschoben um Überlappungen zu vermeiden)
        grade_positions = [
            # Zone 2: Erste Note (als Belohnung für Plattform-Sprung)
            (1300, HEIGHT - 160),  # Über fünfter Plattform (verschoben von PowerUp-Position)
            
            # Zone 3-4: Versteckte Noten (verschoben um PowerUp-Überlappungen zu vermeiden)
            (WIDTH*2 + 420, HEIGHT - 300),    # Über zweiter Plattform statt vierter
            (WIDTH*3 + 550, HEIGHT - 280),    # Über neunter Plattform statt achter
            
            # Zone 5-6: Schwierige Noten (verschoben)
            (WIDTH*4 + 310, HEIGHT - 340),    # Über zweiter Plattform (andere Position)
            (WIDTH*5 + 210, HEIGHT - 240),    # Über siebter Plattform statt neunter
            
            # Zone 7-8: Sehr schwer Belohnungen (verschoben)
            (WIDTH*6 + 350, HEIGHT - 340),    # Über zweiter Plattform statt sechster
            (WIDTH*7 + 140, HEIGHT - 280),    # Über fünfter Plattform statt achter
            
            # Zone 9-10: Expert Belohnungen (verschoben)
            (WIDTH*8 + 270, HEIGHT - 360),    # Über zweiter Plattform statt zehnter
            (WIDTH*9 + 380, HEIGHT - 320),    # Über elfter Plattform statt zehnter
            
            # Zone 11-12: Nightmare Belohnungen (verschoben)
            (WIDTH*10 + 210, HEIGHT - 360),   # Über zweiter Plattform statt vierter
            (WIDTH*11 + 160, HEIGHT - 260),   # Über elfter Plattform statt zwölfter
            
            # Zone 13-14: Extreme Belohnungen (verschoben)
            (WIDTH*12 + 180, HEIGHT - 380),   # Über zweiter Plattform statt zehnter
            (WIDTH*13 + 140, HEIGHT - 380),   # Über zwölfter Plattform statt vierzehnter
            
            # Zone 15-16: Final Boss Belohnungen (verschoben)
            (WIDTH*15 + 220, HEIGHT - 340),   # Über sechster Boss-Arena Plattform statt achter
            (WIDTH*15 + 720, HEIGHT - 200),   # Über letzter Boss-Arena Plattform (verschoben)
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
        # Plattformen (mit Shake-Effekt für brechende Plattformen)
        for platform in self.platforms:
            if hasattr(platform, 'get_render_rect'):
                # Brechende Plattform mit Shake-Effekt
                render_rect = platform.get_render_rect()
                screen.blit(platform.image, self.camera.apply_rect(render_rect))
            else:
                # Normale Plattform
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

        #Betäubung
        if self.player.is_stunned:
            stun_overlay = pygame.Surface(self.player.rect.size, pygame.SRCALPHA)

            stun_overlay.fill((255,0,0,80))
            screen.blit(stun_overlay, player_pos)

    
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