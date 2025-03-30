import pygame
import sys
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BACKGROUND_IMAGE, BACKGROUND_MUSIC
from .menu import main_menu
from .game_loop import game_loop

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Mutators")
    clock = pygame.time.Clock()

    try:
        bg_img = pygame.image.load(BACKGROUND_IMAGE).convert()
        bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg_img = None

    try:
        pygame.mixer.music.load(BACKGROUND_MUSIC)
        pygame.mixer.music.play(-1)
    except:
        print("Warning: Could not load or play background music.")

    font_small = pygame.font.SysFont("Arial", 24, bold=True)
    font_large = pygame.font.SysFont("Arial", 48, bold=True)

    while True:
        main_menu(screen, clock, font_large, font_small)
        game_loop(screen, clock, font_small, bg_img)
