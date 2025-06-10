# Settings: Zentrale Konfiguration für das gesamte Spiel
# Diese Datei enthält alle Konstanten und Einstellungen

# Bildschirm-Einstellungen
WIDTH = 800       # Breite des Bildschirms in Pixeln
HEIGHT = 600      # Höhe des Bildschirms in Pixeln
FPS = 60          # Frames per Second (30 oder 60 FPS sind üblicher Standard)
USE_SCALED = True # Pygame SCALED für Retro-Pixel-Effekt

# Physik-Einstellungen
GRAVITY = 0.8     # Schwerkraftskonstante

# Spieler-Einstellungen
PLAYER_LIVES = 3                    # Anzahl Leben
PLAYER_JUMP_STRENGTH = -15          # Sprungkraft (negativ = nach oben)
PLAYER_SPEED = 5                    # Bewegungsgeschwindigkeit
PLAYER_INVINCIBILITY_TIME = 120     # Unverwundbarkeit in Frames (2 Sek bei 60 FPS)

# Waffen-Einstellungen
WEAPON_COOLDOWN = 30               # Frames zwischen Schüssen
BUBBLE_SPEED = 5                   # Geschwindigkeit der Blasen
BUBBLE_LIFETIME = 180              # Lebensdauer der Blasen in Frames

# Enemy-Einstellungen
ENEMY_SPEED = 2                    # Standard-Geschwindigkeit der Gegner
ENEMY_HEALTH = 100                 # Standard-Gesundheit

# Farben (RGB-Werte)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_GOLD = (255, 215, 0)
COLOR_PURPLE = (255, 0, 255)

# UI-Farben
COLOR_HEART = COLOR_RED
COLOR_PLATFORM = COLOR_GREEN
COLOR_BUBBLE = (100, 200, 255, 180)
COLOR_BACKGROUND = COLOR_BLACK

# Pfade
IMAGE_FOLDER = "images"
SOUND_FOLDER = "sounds" 