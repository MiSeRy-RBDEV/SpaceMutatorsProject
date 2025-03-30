import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
PLAYER_SPRITE = os.path.join(ASSETS_DIR, "player.png")
ENEMY_SPRITES = [
    os.path.join(ASSETS_DIR, "enemy1.png"),
    os.path.join(ASSETS_DIR, "enemy2.png"),
    os.path.join(ASSETS_DIR, "enemy3.png")
]
BACKGROUND_IMAGE = os.path.join(ASSETS_DIR, "background.png")
BACKGROUND_MUSIC = os.path.join(ASSETS_DIR, "background_music.mp3")
