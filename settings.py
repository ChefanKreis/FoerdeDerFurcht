# Settings: Zentrale Konfiguration für das gesamte Spiel
# Diese Datei enthält alle Konstanten und Einstellungen

# Bildschirm-Einstellungen
WIDTH = 800       # Breite des Bildschirms in Pixeln
HEIGHT = 600      # Höhe des Bildschirms in Pixeln
FPS = 60          # Frames per Second (30 oder 60 FPS sind üblicher Standard)
USE_SCALED = True # Pygame SCALED für Retro-Pixel-Effekt

# Physik-Einstellungen
GRAVITY = 0.8     # Schwerkraftskonstante
MAX_FALL_SPEED = 15  # Maximale Fallgeschwindigkeit

# Spieler-Einstellungen
PLAYER_LIVES = 3                  # Anzahl Leben
PLAYER_JUMP_STRENGTH = -15          # Sprungkraft (negativ = nach oben)
PLAYER_SPEED = 5                    # Bewegungsgeschwindigkeit
PLAYER_INVINCIBILITY_TIME = 120     # Unverwundbarkeit in Frames (2 Sek bei 60 FPS)

# Waffen-Einstellungen
WEAPON_COOLDOWN = 30             # Cooldown zwischen Schüssen (in Frames)
BUBBLE_SPEED = 7                 # Geschwindigkeit der Blasen (schneller als Player)
BUBBLE_LIFETIME = 300            # Lebensdauer der Blasen (in Frames)
BUBBLE_RISE_SPEED = 2            # Geschwindigkeit beim Aufsteigen mit gefangenem Gegner
BUBBLE_AUTO_RISE_DELAY = 60      # Frames bis automatischer Aufstieg beginnt
BUBBLE_SPAWN_DISTANCE = 30       # Abstand vom Spieler beim Schießen

# PowerUp-Timer (in Frames bei 60 FPS)
DOUBLE_ESPRESSO_DURATION = 300   # 5 Sekunden
CHEATSHEET_DURATION = 180        # 3 Sekunden  
SEMESTERBREAK_DURATION = 300     # 5 Sekunden

# Enemy-Einstellungen
ENEMY_SPEED = 1                    # Standard-Geschwindigkeit der Gegner
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