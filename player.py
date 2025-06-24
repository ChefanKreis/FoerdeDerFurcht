import pygame
from character import Character
from weapons import Weapon
from settings import PLAYER_LIVES, PLAYER_INVINCIBILITY_TIME, PLAYER_SPEED

class Player(Character):
    def __init__(self, x, y, sprites):
        # Sprites-Dictionary für Animationen speichern
        self.sprites = sprites if sprites else {}
        
        # Standard-Sprite für Character-Initialisierung verwenden
        default_sprite = sprites.get('idle') if sprites else None
        super().__init__(x, y, default_sprite)
        
        # Animation-System
        self.current_animation = 'idle'
        self.facing_direction = 1  # 1 = rechts, -1 = links
        self.shoot_direction = 1   # Separate Schießrichtung
        self.lives = PLAYER_LIVES
        self.weapon = Weapon(self)
        self.is_invincible = False
        self.invincibility_timer = 0  # Timer für Unverwundbarkeit
        
        # Score-System
        self.score = 0
        self.credit_points = 0
        self.grades_collected = 0
        
        # PowerUp-Effekte und Timer (werden von PowerUps gesetzt)
        self.base_speed = PLAYER_SPEED
        self.current_speed = PLAYER_SPEED
        
        # PowerUp-Timer (werden von PowerUps verwaltet)
        self.double_espresso_timer = 0
        self.cheatsheet_timer = 0
        self.semesterbreak_timer = 0
        
        # PowerUp-Status Flags (werden von PowerUps gesetzt)
        self.is_speed_boosted = False
        self.enemies_frozen = False
        self.has_semesterbreak_aura = False

    def shoot(self, projectiles_group, direction=None):
        # Schießrichtung setzen (getrennt von der Sprite-Richtung)
        if direction is not None:
            self.shoot_direction = direction
        else:
            # Keine Richtung angegeben: Aktuelle facing_direction verwenden
            self.shoot_direction = self.facing_direction
        
        # facing_direction wird NIEMALS durch Schießen geändert!
        # Sie wird nur durch Bewegung in update() bestimmt
        
        # Waffe abfeuern
        return self.weapon.fire(projectiles_group)

    def collect(self, item):
        """Sammelt PowerUps und Collectibles ein - delegiert an die Item-Klassen"""
        if not item:
            return
        
        # PowerUps wenden sich selbst an
        if hasattr(item, 'apply'):
            item.apply(self)
        # Collectibles sammeln sich selbst
        elif hasattr(item, 'collect'):
            item.collect(self)
        
        # Item aus dem Spiel entfernen
        item.kill()
        
        # Debug-Output
        print(f"Gesammelt: {item.type} | Score: {self.score} | CP: {self.credit_points}")

    def take_damage(self, amount=1):
        # Semesterferien-Aura macht unverwundbar
        if self.has_semesterbreak_aura:
            print("Schaden abgewehrt durch Semesterferien-Aura!")
            return
            
        if not self.is_invincible:
            self.lives -= 1
            if self.lives > 0:
                # Leben verloren, aber noch Leben übrig - kurze Unverwundbarkeit
                self.is_invincible = True
                self.invincibility_timer = PLAYER_INVINCIBILITY_TIME
            # Wenn self.lives <= 0, wird das Game Over vom Game-Objekt behandelt

    def update(self, platforms=None):
        # facing_direction wird NUR durch Bewegung bestimmt
        old_facing_direction = self.facing_direction
        
        if self.velocity.x > 0:
            self.facing_direction = 1  # nach rechts
        elif self.velocity.x < 0:
            self.facing_direction = -1  # nach links
        # Bei velocity.x == 0 bleibt facing_direction erhalten
        # shoot_direction bleibt unverändert und wird nur beim Schießen gesetzt
        
        # Animation basierend auf Zustand aktualisieren
        self._update_animation()
        
        # Sprite sofort aktualisieren wenn sich die Richtung geändert hat
        if old_facing_direction != self.facing_direction:
            self._apply_current_sprite()
        
        super().update(platforms)
        self.weapon.update()  # Weapon-Cooldown aktualisieren
        
        # Unverwundbarkeits-Timer verwalten
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.is_invincible = False
        
        # PowerUp-Timer verwalten
        self._update_powerup_timers()
    
    def _update_animation(self):
        """Aktualisiert die Player-Animation basierend auf dem aktuellen Zustand"""
        if not self.sprites:
            return  # Keine Sprites verfügbar
        
        # Animation basierend auf Zustand bestimmen
        new_animation = 'idle'
        
        if not self.on_ground:
            # Spieler ist in der Luft (springend oder fallend)
            new_animation = 'jump'
        elif abs(self.velocity.x) > 0:
            # Spieler bewegt sich horizontal
            new_animation = 'run'
        
        # Animation nur ändern wenn nötig
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self._apply_current_sprite()
    
    def _apply_current_sprite(self):
        """Wendet das aktuelle Sprite mit Richtungs-Spiegelung an"""
        if not self.sprites or self.current_animation not in self.sprites:
            return
        
        # Basis-Sprite holen
        base_sprite = self.sprites[self.current_animation]
        
        # Aktuelle Position merken
        old_center = self.rect.center
        
        # Spiegelung anwenden falls nötig
        if self.facing_direction == -1:
            # Nach links: Sprite horizontal spiegeln
            self.image = pygame.transform.flip(base_sprite, True, False)
        else:
            # Nach rechts: Original-Sprite verwenden
            self.image = base_sprite
        
        # Kollisionsbox an neue Sprite-Größe anpassen (falls sich geändert)
        # und Position beibehalten
        self.rect = self.image.get_rect(center=old_center)
    
    def _update_powerup_timers(self):
        """Verwaltet alle PowerUp-Timer (minimale Timer-Logik, PowerUps setzen die Werte)"""
        
        # Doppelter Espresso Timer
        if self.double_espresso_timer > 0:
            self.double_espresso_timer -= 1
            if self.double_espresso_timer <= 0:
                self.is_speed_boosted = False
                self.current_speed = self.base_speed
                print("Doppelter Espresso-Effekt beendet!")
        
        # Spickzettel-Scroll Timer
        if self.cheatsheet_timer > 0:
            self.cheatsheet_timer -= 1
            if self.cheatsheet_timer <= 0:
                self.enemies_frozen = False
                print("Spickzettel-Scroll-Effekt beendet!")
        
        # Semesterferien-Aura Timer
        if self.semesterbreak_timer > 0:
            self.semesterbreak_timer -= 1
            if self.semesterbreak_timer <= 0:
                self.has_semesterbreak_aura = False
                print("Semesterferien-Aura beendet!")
    
    def get_movement_speed(self):
        """Gibt die aktuelle Bewegungsgeschwindigkeit zurück"""
        return self.current_speed
    
    def are_enemies_frozen(self):
        """Prüft ob Gegner durch Spickzettel-Scroll eingefroren sind"""
        return self.enemies_frozen
    
    def has_active_powerups(self):
        """Prüft ob PowerUps aktiv sind (für visuelle Effekte)"""
        return (self.is_speed_boosted or 
                self.enemies_frozen or 
                self.has_semesterbreak_aura)
    
    def get_powerup_status(self):
        """Gibt den Status aller aktiven PowerUps zurück (für HUD)"""
        status = []
        if self.is_speed_boosted:
            status.append(f"Espresso: {self.double_espresso_timer//60 + 1}s")
        if self.enemies_frozen:
            status.append(f"Spickzettel: {self.cheatsheet_timer//60 + 1}s")
        if self.has_semesterbreak_aura:
            status.append(f"Aura: {self.semesterbreak_timer//60 + 1}s")
        return status

    # Kollisionen mit Plattformen prüfen (wird vom Level aufgerufen) 