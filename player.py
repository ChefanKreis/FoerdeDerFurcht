import pygame
from enemies import Character
from weapons import Weapon
from settings import PLAYER_LIVES, PLAYER_INVINCIBILITY_TIME

class Player(Character):
    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)
        self.lives = PLAYER_LIVES
        self.weapon = Weapon(self)
        self.is_invincible = False
        self.invincibility_timer = 0  # Timer für Unverwundbarkeit

    def shoot(self, projectiles_group):
        # Waffe abfeuern
        return self.weapon.fire(projectiles_group)

    def collect(self, item):
        # TODO: Sammeln
        pass

    def take_damage(self, amount=1):
        if not self.is_invincible:
            self.lives -= 1
            if self.lives > 0:
                # Leben verloren, aber noch Leben übrig - kurze Unverwundbarkeit
                self.is_invincible = True
                self.invincibility_timer = PLAYER_INVINCIBILITY_TIME
            # Wenn self.lives <= 0, wird das Game Over vom Game-Objekt behandelt

    def update(self, platforms=None):
        super().update(platforms)
        self.weapon.update()  # Weapon-Cooldown aktualisieren
        
        # Unverwundbarkeits-Timer verwalten
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.is_invincible = False
        
        # Kollisionen mit Plattformen prüfen (wird vom Level aufgerufen)
        # TODO: Spieler-Eingabe, Zustand prüfen 