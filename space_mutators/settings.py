import os

# Game region
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Additional width for charts on the right
CHART_WIDTH = 300

# Additional heatmap width for charts on the right
HEATMAP_WIDTH = 300

# The total screen width for the entire window
TOTAL_WIDTH = SCREEN_WIDTH + CHART_WIDTH + HEATMAP_WIDTH

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
PLAYER_SPRITE = os.path.join(ASSETS_DIR, "player.png")
ENEMY_SPRITES = [
    os.path.join(ASSETS_DIR, "enemy1.png"),
    os.path.join(ASSETS_DIR, "enemy2.png"),
    os.path.join(ASSETS_DIR, "enemy3.png")
]
BACKGROUND_IMAGE = os.path.join(ASSETS_DIR, "background.png")
BACKGROUND_MUSIC = os.path.join(ASSETS_DIR, "background_music.mp3")
