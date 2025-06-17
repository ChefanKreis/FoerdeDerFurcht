import pygame
from character import Character
from weapons import Weapon
from settings import PLAYER_LIVES, PLAYER_INVINCIBILITY_TIME, PLAYER_SPEED

class Player(Character):
    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)
        self.lives = PLAYER_LIVES
        self.weapon = Weapon(self)
        self.is_invincible = False
        self.invincibility_timer = 0  # Timer für Unverwundbarkeit
        
        # Richtung für Schießen
        self.facing_direction = 1  # 1 = rechts, -1 = links
        
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

    def shoot(self, projectiles_group):
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
        # Richtung basierend auf Bewegung aktualisieren
        if self.velocity.x > 0:
            self.facing_direction = 1  # nach rechts
        elif self.velocity.x < 0:
            self.facing_direction = -1  # nach links
        # Bei velocity.x == 0 bleibt die letzte Richtung erhalten
        
        super().update(platforms)
        self.weapon.update()  # Weapon-Cooldown aktualisieren
        
        # Unverwundbarkeits-Timer verwalten
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.is_invincible = False
        
        # PowerUp-Timer verwalten
        self._update_powerup_timers()
    
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
    # TODO: Spieler-Eingabe, Zustand prüfen 