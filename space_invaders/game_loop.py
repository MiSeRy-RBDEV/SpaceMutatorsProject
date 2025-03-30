import pygame
import sys
import random
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, TOTAL_WIDTH
from .sprite_defs import Player, Enemy, Bullet, EnemyChromosome
from .utils import draw_text

def draw_chromosome_stats(screen, x_offset, y_offset, width, height, font, chromosomes):
    """
    Draw a simple bar chart of the average gene values in 'chromosomes'
    at position (x_offset, y_offset) with total region (width, height).
    """

    # Fill the chart area with black to clear previous frame
    chart_rect = pygame.Rect(x_offset, y_offset, width, height)
    pygame.draw.rect(screen, (30, 30, 30), chart_rect)

    if not chromosomes:
        draw_text("No data", font, WHITE, screen, x_offset + width // 2, y_offset + height // 2)
        return

    # 1) Compute average values for each gene
    avg_speed = sum(c.speed_gene for c in chromosomes) / len(chromosomes)
    avg_health = sum(c.health_gene for c in chromosomes) / len(chromosomes)
    avg_bullet = sum(c.bullet_speed_gene for c in chromosomes) / len(chromosomes)
    avg_scale = sum(c.sprite_scale_gene for c in chromosomes) / len(chromosomes)
    avg_color = sum(c.color_tint_gene for c in chromosomes) / len(chromosomes)

    # 2) We’ll create bar charts for these 5 genes.
    # Let's define some reference maximums for each gene for scaling:
    # (you can tweak these as you see fit)
    max_speed = 10
    max_health = 5
    max_bullet = 20
    max_scale = 200
    max_color = 255

    # We'll store these in a list of tuples: (name, avg, max)
    data = [
        ("Speed", avg_speed, max_speed),
        ("Health", avg_health, max_health),
        ("Bullet", avg_bullet, max_bullet),
        ("Scale", avg_scale, max_scale),
        ("Tint", avg_color, max_color),
    ]

    # 3) Draw each bar
    # We'll distribute bars vertically. Each bar ~ 40 px high, with spacing.
    bar_height = 40
    spacing = 10
    start_y = y_offset + 30  # a little space from the top

    for i, (label, avg_val, max_val) in enumerate(data):
        # Where to draw this bar?
        bar_top = start_y + i * (bar_height + spacing)
        # Scale the bar width according to the average / max
        fraction = avg_val / max_val if max_val > 0 else 0
        bar_w = int(width * 0.8 * fraction)  # 80% of chart width is for bars

        # Draw background bar
        bg_rect = pygame.Rect(x_offset + 10, bar_top, int(width * 0.8), bar_height)
        pygame.draw.rect(screen, (80, 80, 80), bg_rect)

        # Draw filled portion
        fill_rect = pygame.Rect(x_offset + 10, bar_top, bar_w, bar_height)
        pygame.draw.rect(screen, (100, 200, 100), fill_rect)

        # Draw label
        draw_text(f"{label}: {avg_val:.1f}", font, WHITE, screen, x_offset + width // 2, bar_top + bar_height // 2)

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

    # Keep track of chromosomes for breeding
    died_chromosomes = []

    while True:
        clock.tick(FPS)

        # End conditions
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

        # Spawn enemies
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            if len(died_chromosomes) >= 2 and random.random() < 0.7:
                # 70% chance to spawn from breeding
                parentA = random.choice(died_chromosomes)
                parentB = random.choice(died_chromosomes)
                child_chrom = EnemyChromosome.crossover(parentA, parentB)
                child_chrom.mutate(mutation_rate=0.15)
                enemy = Enemy(level, chromosome=child_chrom)
            else:
                # random chromosome
                enemy = Enemy(level)
            all_sprites.add(enemy)
            enemies.add(enemy)

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        # Check if enemies escaped
        for enemy in enemies.copy():
            if enemy.rect.top > SCREEN_HEIGHT:
                # We treat escaping as a success for the enemy
                enemy.chromosome.add_fitness(100)
                escaped_enemies += 1
                died_chromosomes.append(enemy.chromosome)
                enemy.kill()

        enemies.update()
        bullets.update()

        # Bullet-enemy collisions
        collisions = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for enemy in collisions.keys():
            score += 1
            enemy.chromosome.add_fitness(-20)  # penalize being shot
            died_chromosomes.append(enemy.chromosome)

        # Enemy-player collisions
        collided_enemies = pygame.sprite.spritecollide(player, enemies, True)
        for enemy in collided_enemies:
            player.health -= 20
            enemy.chromosome.add_fitness(50)   # reward them for hitting player
            died_chromosomes.append(enemy.chromosome)

        # Drawing
        if bg_img:
            # Draw the background so it covers the entire 900x600
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(BLACK)

        # Draw all sprites in the left side (0..SCREEN_WIDTH)
        all_sprites.draw(screen)
        player.draw_health_bar(screen)

        # Score / Level / Escaped text also on the left side
        draw_text(f"Score: {score}", font_small, WHITE, screen, 60, 20)
        draw_text(f"Level: {level}", font_small, WHITE, screen, SCREEN_WIDTH - 60, 20)
        draw_text(f"Escaped: {escaped_enemies}/{max_escaped}", font_small, WHITE, screen, SCREEN_WIDTH // 2, 20)

        # =====================
        # == Right Panel Charts
        # =====================
        # We combine living + died chromosomes to get an overall sense of the gene pool
        all_chromosomes = [enemy.chromosome for enemy in enemies] + died_chromosomes

        # Draw the stats area in the region x=SCREEN_WIDTH..TOTAL_WIDTH
        chart_x = SCREEN_WIDTH
        chart_y = 0
        chart_w = TOTAL_WIDTH - SCREEN_WIDTH
        chart_h = SCREEN_HEIGHT

        draw_chromosome_stats(screen, chart_x, chart_y, chart_w, chart_h, font_small, all_chromosomes)

        pygame.display.flip()
