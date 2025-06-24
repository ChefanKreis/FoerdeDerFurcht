import pygame
from settings import (WIDTH, HEIGHT, WEAPON_COOLDOWN, BUBBLE_SPEED, BUBBLE_LIFETIME, 
                      COLOR_BLUE, COLOR_BUBBLE, BUBBLE_RISE_SPEED, BUBBLE_AUTO_RISE_DELAY,
                      BUBBLE_SPAWN_DISTANCE)

class Weapon:
    def __init__(self, owner):
        self.owner = owner
        self.cooldown = 0
        self.max_cooldown = WEAPON_COOLDOWN

    def fire(self, projectiles_group):
        if self.cooldown <= 0:
            # Schießrichtung vom Player übernehmen (falls verfügbar)
            if hasattr(self.owner, 'shoot_direction'):
                direction = self.owner.shoot_direction
            elif hasattr(self.owner, 'facing_direction'):
                direction = self.owner.facing_direction
            else:
                # Fallback: Richtung basierend auf aktueller Bewegung
                direction = 1  # Standard: nach rechts
                if self.owner.velocity.x < 0:
                    direction = -1  # nach links
                elif self.owner.velocity.x == 0:
                    direction = 1  # Standard: nach rechts wenn keine Bewegung
            
            # Neue Blase seitlich vom Spieler erzeugen
            bubble = Bubble(
                self.owner.rect.centerx + (direction * BUBBLE_SPAWN_DISTANCE),  # Konfigurierbare Distanz
                self.owner.rect.centery,  # Auf gleicher Höhe wie der Spieler
                direction,  # Richtung an die Blase übergeben
                level_width=self.owner.level_width  # Level-Breite übergeben
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
        if sprite is None:
            self.image.fill(COLOR_BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = pygame.math.Vector2(0, -5)

    def update(self, *args, **kwargs):
        # Die Logik zum Entfernen außerhalb des Bildschirms wird jetzt
        # von der Bubble-Klasse selbst gehandhabt, da diese die Kamera
        # berücksichtigen muss.
        self.rect.move_ip(self.velocity)
        # HINWEIS: Das Entfernen des Projektils außerhalb des Levels
        # (nicht nur des Bildschirms) wird jetzt in der Bubble-Klasse gemacht.

class Bubble(Projectile):
    def __init__(self, x, y, direction=1, captured_enemy=None, level_width=WIDTH):
        super().__init__(x, y, None)
        
        # Versuche bubble.png zu laden
        try:
            self.base_image = pygame.image.load("images/bubble.png").convert_alpha()
            # Skaliere auf passende Größe (20x20 für normale Blase)
            self.image = pygame.transform.scale(self.base_image, (20, 20))
            print("Bubble-Sprite geladen: images/bubble.png")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Bubble-Sprite 'bubble.png' konnte nicht geladen werden: {e}")
            # Fallback: Gezeichnete Blase
            self.base_image = None
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, COLOR_BUBBLE, (10, 10), 10, 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = pygame.math.Vector2(direction * BUBBLE_SPEED, 0)  # Horizontale Bewegung
        self.captured_enemy = captured_enemy
        self.lifetime = BUBBLE_LIFETIME
        self.rising = False  # Flag für Aufstieg-Modus
        self.pop_timer = 0   # Timer für Platzen-Animation
        self.is_popping = False  # Flag für Platzen-Zustand
        self.level_width = level_width
        
    def update(self, camera=None):
        if self.is_popping:
            self._handle_popping()
            return
            
        # Normale Bewegung
        if not self.rising:
            # Horizontale Bewegung (normal)
            self.rect.x += self.velocity.x
        else:
            # Aufstieg-Bewegung (mit gefangenem Gegner)
            self.rect.y -= BUBBLE_RISE_SPEED  # Langsam nach oben steigen
            # Gefangenen Gegner mitbewegen
            if self.captured_enemy:
                self.captured_enemy.rect.center = self.rect.center
        
        # Lebensdauer verringern
        self.lifetime -= 1
        
        # Bildschirmgrenzen und Lebensdauer prüfen und ggf. platzen
        if self._should_be_removed(camera):
            self.pop(give_points=False) # Am Rand platzen gibt keine Punkte
    
    def _should_be_removed(self, camera=None):
        """Prüft, ob die Blase entfernt werden soll (platzt am Bildschirmrand)."""
        # Lebensdauer abgelaufen
        if self.lifetime <= 0:
            return True
        
        # Wenn eine Kamera übergeben wird, prüfe gegen den Bildschirmrand
        if camera:
            screen_rect = camera.apply(self)
            
            # Horizontale Prüfung gegen den Bildschirmrand
            if not self.rising and (screen_rect.right < 0 or screen_rect.left > WIDTH):
                return True
            
            # Vertikale Prüfung (nur nach oben relevant für aufsteigende Blasen)
            if screen_rect.bottom < 0:
                return True
        
        # Fallback auf Level-Grenzen, falls keine Kamera vorhanden ist
        else:
            if not self.rising and (self.rect.right < 0 or self.rect.left > self.level_width):
                return True
            if self.rect.bottom < 0 or self.rect.top > HEIGHT:
                return True
            
        return False
    
    def _remove_bubble(self):
        """Entfernt die Blase und behandelt gefangene Gegner"""
        if self.captured_enemy and not self.is_popping:
            # Gegner "besiegen" (entfernen)
            if hasattr(self.captured_enemy, 'kill'):
                self.captured_enemy.kill()
        self.kill()
    
    def capture_enemy(self, enemy):
        """Fängt einen Gegner in der Blase"""
        if not self.captured_enemy and not self.is_popping:
            self.captured_enemy = enemy
            # Gegner in die Blase einschließen
            enemy.rect.center = self.rect.center
            enemy.velocity = pygame.math.Vector2(0, 0)  # Gegner kann sich nicht bewegen
            
            # Blase wird größer mit gefangenem Gegner
            if self.base_image:
                # Verwende Sprite-Textur, größer skaliert
                self.image = pygame.transform.scale(self.base_image, (30, 30))
                # Gegner in der Blase zeichnen (kleiner)
                enemy_mini = pygame.transform.scale(enemy.image, (20, 20))
                self.image.blit(enemy_mini, (5, 5))
            else:
                # Fallback: Gezeichnete Blase
                self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(self.image, COLOR_BUBBLE, (15, 15), 15, 2)
                # Gegner in der Blase zeichnen (kleiner)
                enemy_mini = pygame.transform.scale(enemy.image, (20, 20))
                self.image.blit(enemy_mini, (5, 5))
            
            self.rect = self.image.get_rect(center=self.rect.center)
            
            # Gegner aus der normalen Update-Schleife entfernen
            enemy.kill()
            
            # Nach kurzer Zeit beginnt die Blase zu steigen
            self.lifetime = max(self.lifetime, 120)  # Mindest-Lebensdauer für Aufstieg
            
    def start_rising(self):
        """Startet den Aufstieg der Blase (automatisch nach Gegner-Fang)"""
        if self.captured_enemy:
            self.rising = True
            self.velocity.x = 0  # Horizontale Bewegung stoppen
    
    def pop(self, give_points=True):
        """Lässt die Blase platzen"""
        if not self.is_popping:
            self.is_popping = True
            self.pop_timer = 30  # 0.5 Sekunden bei 60 FPS
            
            # Platzen-Animation: Blase wird größer und transparenter
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            # Platzen-Effekt zeichnen
            pygame.draw.circle(self.image, (255, 255, 255, 100), (20, 20), 20, 3)
            pygame.draw.circle(self.image, (200, 200, 255, 150), (20, 20), 15, 2)
            self.rect = self.image.get_rect(center=self.rect.center)
            
            # Punkte geben falls Gegner gefangen war
            if self.captured_enemy and give_points:
                # TODO: Hier könnte Score-System implementiert werden
                print(f"Gegner besiegt! +100 Punkte")  # Debug-Output
                
            # Gefangenen Gegner "besiegen"
            if self.captured_enemy:
                self.captured_enemy.kill()
                self.captured_enemy = None
    
    def _handle_popping(self):
        """Behandelt die Platzen-Animation"""
        self.pop_timer -= 1
        if self.pop_timer <= 0:
            self.kill()
    
    def can_be_popped(self):
        """Prüft ob die Blase geplatzt werden kann (von anderen Blasen oder Spieler)"""
        return not self.is_popping
    
    def update_rising_logic(self):
        """Automatische Aufstieg-Logik - wird vom Level aufgerufen"""
        if self.captured_enemy and not self.rising and not self.is_popping:
            # Nach konfigurierter Zeit mit gefangenem Gegner automatisch steigen
            if self.lifetime < BUBBLE_LIFETIME - BUBBLE_AUTO_RISE_DELAY:
                self.start_rising()

    def release_enemy(self):
        """Gibt gefangenen Gegner wieder frei (bei vorzeitigem Platzen ohne Besiegen)"""
        if self.captured_enemy and not self.is_popping:
            # Gegner wieder in die Spielwelt setzen
            # TODO: Hier könnte man den Gegner wieder zur enemies-Gruppe hinzufügen
            # Für jetzt wird der Gegner einfach "besiegt"
            self.captured_enemy.kill()
            self.captured_enemy = None 

class RedPen(Projectile):
    def __init__(self, x, y, target_player):
        #Lade das Sprite (oder erstelle ein Fallback-Rechteck)
        sprite = None
        try:
            sprite = pygame.image.load("images/red_pen.png").convert_alpha()
            sprite = pygame.transform.scale(sprite, (30, 15))
        except (pygame.error, FileNotFoundError):
            print("Fehler: 'red_pen.png' konnte nicht geladen werden. Nutze Fallback.")
            sprite = pygame.Surface((15, 5))
            sprite.fill((255, 50, 50))

        super().__init__(x, y, sprite)

        #Berechne die Geschwindigkeit und speichere sie in dieser Instanz
        direction = pygame.math.Vector2(target_player.rect.centerx - self.rect.centerx,
                                        target_player.rect.centery - self.rect.centery)
        if direction.length() > 0:
            direction.normalize_ip()

        speed = 8
        self.velocity = direction * speed # Speichere den Geschwindigkeitsvektor

    def update(self, camera=None):
        #Update Methode bewegt Projektil
        self.rect.move_ip(self.velocity)

        #Lösche das Projektil, wenn es weit außerhalb des Bildschirms ist
        if camera and not camera.camera_rect.colliderect(self.rect):
            if self.rect.bottom < 0 or self.rect.top > camera.level_height or \
               self.rect.right < 0 or self.rect.left > camera.level_width:
                self.kill()