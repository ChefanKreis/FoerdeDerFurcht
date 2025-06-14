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
from enemies import MultipleChoiceEnemy, PythonEnemy, ProgrammingTaskEnemy
from movement_enemies import MovementStrategy, HorizontalMovement, RandomJump, ChasePlayer
from weapons import Weapon, Bubble
from platforms import Platform
from powerups import *

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
        self.player = Player(100, 400, None)  # Platzhalter für Sprite

        self.enemies = pygame.sprite.Group()
        enemy = MultipleChoiceEnemy(200, 300, None)  # Beispielgegner
        self.enemies.add(enemy)
        # Weitere Gegner möglich

        self.powerups = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()  # Gruppe für Projektile/Blasen
        self.load()

    def load(self):
        # TODO: Layout, Gegner, PowerUps etc. basierend auf Level-Number laden
        # Temporäre Test-Plattformen hinzufügen
        self.platforms.add(Platform(0, HEIGHT - 50, WIDTH, 50))  # Boden
        self.platforms.add(Platform(200, HEIGHT - 150, 200, 20))  # Plattform 1
        self.platforms.add(Platform(500, HEIGHT - 250, 150, 20))  # Plattform 2
        
        # Test-PowerUps spawnen
        self._spawn_test_items()

    def update(self):
        self.player.update(self.platforms)
        
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
    
    def _spawn_test_items(self):
        """Spawnt Test-PowerUps und Collectibles für das Demo-Level"""
        from powerups import (DoubleEspresso, CheatsheetScroll, SemesterbreakAura, 
                             MotivationFishBread, Creditpoint, Grade)
        
        # PowerUps an verschiedenen Positionen
        self.powerups.add(DoubleEspresso(300, HEIGHT - 200))        # Auf Plattform 1
        self.powerups.add(CheatsheetScroll(550, HEIGHT - 300))      # Auf Plattform 2
        self.powerups.add(SemesterbreakAura(150, HEIGHT - 100))     # Am Boden
        self.powerups.add(MotivationFishBread(650, HEIGHT - 100))   # Am Boden rechts
        
        # Credit Points verteilt
        for i in range(5):
            self.collectibles.add(Creditpoint(100 + i*100, HEIGHT - 100))
        
        # Eine versteckte Grade (1,0-Note)
        self.collectibles.add(Grade(400, HEIGHT - 180))  # Versteckt auf Plattform

    def draw(self, screen):
        # Alle Sprites zeichnen
        self.platforms.draw(screen)
        self.collectibles.draw(screen)
        self.powerups.draw(screen)
        
        # Gegner zeichnen (mit Einfrieren-Effekt)
        for enemy in self.enemies:
            if self.player.are_enemies_frozen():
                # Gefrorene Gegner: Bläulicher Tint
                frozen_surface = enemy.image.copy()
                frozen_overlay = pygame.Surface(frozen_surface.get_size())
                frozen_overlay.fill((100, 150, 255))  # Blauer Tint
                frozen_overlay.set_alpha(100)
                frozen_surface.blit(frozen_overlay, (0, 0))
                screen.blit(frozen_surface, enemy.rect)
            else:
                screen.blit(enemy.image, enemy.rect)
        
        self.projectiles.draw(screen)  # Projektile zeichnen
        
        # Spieler zeichnen (mit Effekten)
        self._draw_player_with_effects(screen)
    
    def _draw_player_with_effects(self, screen):
        """Zeichnet den Spieler mit allen aktiven visuellen Effekten"""
        player_surface = self.player.image.copy()
        
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
                screen.blit(player_surface, self.player.rect)
        else:
            screen.blit(player_surface, self.player.rect)

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