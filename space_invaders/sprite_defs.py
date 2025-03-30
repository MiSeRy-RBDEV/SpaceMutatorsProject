import pygame
import random
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GREEN, RED, PLAYER_SPRITE, ENEMY_SPRITES

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(PLAYER_SPRITE).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
        self.health = 100
        self.max_health = 100

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if pressed_keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw_health_bar(self, surface):
        bar_length = 100
        bar_height = 10
        fill = (self.health / self.max_health) * bar_length
        outline_rect = pygame.Rect(self.rect.centerx - bar_length//2, self.rect.bottom + 10, bar_length, bar_height)
        fill_rect = pygame.Rect(self.rect.centerx - bar_length//2, self.rect.bottom + 10, fill, bar_height)
        pygame.draw.rect(surface, RED, outline_rect)
        pygame.draw.rect(surface, GREEN, fill_rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        sprite_index = min(level - 1, len(ENEMY_SPRITES) - 1)
        self.image = pygame.image.load(ENEMY_SPRITES[sprite_index]).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5) + level

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()
