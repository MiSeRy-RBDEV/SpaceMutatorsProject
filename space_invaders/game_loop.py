import pygame
import sys
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE
from .sprite_defs import Player, Enemy, Bullet
from .utils import draw_text

def game_loop(screen, clock, font_small, bg_img):
    level = 1
    max_levels = 3
    player = Player()
    all_sprites = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    score = 0
    spawn_timer = 0
    escaped_enemies = 0
    max_escaped = 10
    spawn_interval = 60

    while True:
        clock.tick(FPS)
        if player.health <= 0 or escaped_enemies >= max_escaped:
            return
        if score >= 20 * level and level < max_levels:
            level += 1
        if level > max_levels:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)

        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            enemy = Enemy(level)
            all_sprites.add(enemy)
            enemies.add(enemy)

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        # Track escaped enemies
        for enemy in enemies.copy():
            if enemy.rect.top > SCREEN_HEIGHT:
                enemy.kill()
                escaped_enemies += 1


        enemies.update()
        bullets.update()

        # Bullet-enemy collisions
        for _ in pygame.sprite.groupcollide(enemies, bullets, True, True):
            score += 1

        # Enemy-player collisions
        for _ in pygame.sprite.spritecollide(player, enemies, True):
            player.health -= 20

        # Drawing
        if bg_img: screen.blit(bg_img, (0, 0))
        else: screen.fill(BLACK)
        all_sprites.draw(screen)
        player.draw_health_bar(screen)

        draw_text(f"Score: {score}", font_small, WHITE, screen, 60, 20)
        draw_text(f"Level: {level}", font_small, WHITE, screen, SCREEN_WIDTH - 60, 20)
        draw_text(f"Escaped: {escaped_enemies}/{max_escaped}", font_small, WHITE, screen, SCREEN_WIDTH // 2, 20)

        pygame.display.flip()