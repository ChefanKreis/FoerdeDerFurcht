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
        # Font für Text-Darstellung
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.title_font = pygame.font.Font(None, 48)
        
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
        
        # Fallback wird automatisch in draw_start_screen() verwendet

    def start(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.show_start_screen:
                    # Startbildschirm: Beliebige Taste startet das Spiel
                    self.show_start_screen = False
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
        self.show_start_screen = True  # Zurück zum Startbildschirm

class Level:
    def __init__(self, number):
        self.number = number
        self.layout = None  # Level-Daten laden
        
        # Level-Größe (größer als der Bildschirm für Scrolling)
        self.level_width = WIDTH * 3 # 3x so breit wie der Bildschirm
        self.level_height = HEIGHT
        
        # Kamera initialisieren
        self.camera = Camera(self.level_width, self.level_height)
        
        self.player = Player(100, 400, None)  # Platzhalter für Sprite
        
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
        
        self.load()

    def load(self):
        # Erweiterte Level-Generierung für Scrolling
        # Boden über die gesamte Level-Breite
        ground_height = 50
        self.platforms.add(Platform(0, HEIGHT - ground_height, self.level_width, ground_height))
        
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
                enemy = MultipleChoiceEnemy(x, y, None, self.level_width) # Pass level_width
            elif i % 3 == 1:
                enemy = PythonEnemy(x, y, None, self.level_width) # Pass level_width
            else:
                enemy = ProgrammingTaskEnemy(x, y, None, self.level_width) # Pass level_width
            
            self.enemies.add(enemy)
                
        ######## Boss am Ende hinzufügen ########
        boss_x = self.level_width - 300  # Boss am rechten Ende des Levels
        boss_y = HEIGHT - 200  # Etwas höher als der Boden
        boss = Boss(boss_x, boss_y, None, self.level_width)  # Pass level_width
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

        # Kollision Spieler mit Enemies
        if self.player.rect.colliderect(enemy.rect):
            if not self.player.is_invincible:
                self.player.take_damage()
        
        self.powerups.update()
        self.collectibles.update()
        self.platforms.update()
        self.projectiles.update()  # Projektile aktualisieren
        
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
        player_surface = self.player.image.copy()
        player_pos = self.camera.apply(self.player)
        
        # PowerUp-Effekte
        if self.player.is_speed_boosted:
            # Geschwindigkeits-Effekt: Gelber Umriss
            speed_overlay = pygame.Surface(player_surface.get_size())
            speed_overlay.fill((255, 255, 0))  # Gelb
            speed_overlay.set_alpha(80)
            player_surface.blit(speed_overlay, (0, 0))
        
        if self.player.has_semesterbreak_aura:
            # Unverwundbarkeits-Effekt: Grüner Schimmer
            aura_overlay = pygame.Surface(player_surface.get_size())
            aura_overlay.fill((0, 255, 0))  # Grün
            aura_overlay.set_alpha(60)
            player_surface.blit(aura_overlay, (0, 0))
        
        # Unverwundbarkeits-Blinken
        if self.player.is_invincible:
            # Blinken: Nur jede 10 Frames zeichnen
            if (self.player.invincibility_timer // 5) % 2 == 0:
                screen.blit(player_surface, player_pos)
        else:
            screen.blit(player_surface, player_pos)

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