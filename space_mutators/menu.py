import pygame
import sys
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, BACKGROUND_IMAGE, BACKGROUND_MUSIC
from .utils import draw_text

def main_menu(screen, clock, font_large, font_small):
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

    while True:
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(BLACK)

        draw_text("SPACE MUTATORS", font_large, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text("ALIENS SHIPS ARE ATTACKING OUR PLANET", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
        draw_text("STOP THEM AND SAVE THE PLANET", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90)
        draw_text("Press [SPACE] to START or [Q] to QUIT", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160)

        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
