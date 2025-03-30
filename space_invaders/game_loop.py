import pygame
import sys
import random
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, TOTAL_WIDTH
from .sprite_defs import Player, Enemy, Bullet, EnemyChromosome
from .utils import draw_text

# 1) A global list to track average fitness over time.
fitness_history = []

def draw_chromosome_stats(screen, x_offset, y_offset, width, height, font, chromosomes):
    """
    Already defined in your code: draws a bar chart of gene averages.
    We'll leave it as is.
    """
    # Example implementation from your existing code:
    pygame.draw.rect(screen, (30, 30, 30), (x_offset, y_offset, width, height))

    if not chromosomes:
        draw_text("No data", font, WHITE, screen, x_offset + width // 2, y_offset + height // 2)
        return

    avg_speed = sum(c.speed_gene for c in chromosomes) / len(chromosomes)
    avg_health = sum(c.health_gene for c in chromosomes) / len(chromosomes)
    avg_bullet = sum(c.bullet_speed_gene for c in chromosomes) / len(chromosomes)
    avg_scale = sum(c.sprite_scale_gene for c in chromosomes) / len(chromosomes)
    avg_color = sum(c.color_tint_gene for c in chromosomes) / len(chromosomes)

    max_speed = 10
    max_health = 5
    max_bullet = 20
    max_scale = 200
    max_color = 255

    data = [
        ("Speed", avg_speed, max_speed),
        ("Health", avg_health, max_health),
        ("Bullet", avg_bullet, max_bullet),
        ("Scale", avg_scale, max_scale),
        ("Tint", avg_color, max_color),
    ]

    bar_height = 30
    spacing = 10
    start_y = y_offset + 20

    for i, (label, avg_val, max_val) in enumerate(data):
        bar_top = start_y + i * (bar_height + spacing)
        fraction = avg_val / max_val if max_val > 0 else 0
        bar_w = int(width * 0.8 * fraction)

        # Draw background bar
        bg_rect = pygame.Rect(x_offset + 10, bar_top, int(width * 0.8), bar_height)
        pygame.draw.rect(screen, (80, 80, 80), bg_rect)

        # Draw filled portion
        fill_rect = pygame.Rect(x_offset + 10, bar_top, bar_w, bar_height)
        pygame.draw.rect(screen, (100, 200, 100), fill_rect)

        # Draw label text
        draw_text(f"{label}: {avg_val:.1f}", font, WHITE, screen, x_offset + width // 2, bar_top + bar_height // 2)

def draw_fitness_chart(screen, x_offset, y_offset, width, height, font):
    """
    2) A new function that draws a simple line chart of fitness_history.
    Each entry in fitness_history is an average fitness for one frame (or wave).
    """
    # Clear background for the chart region
    chart_rect = pygame.Rect(x_offset, y_offset, width, height)
    pygame.draw.rect(screen, (20, 20, 20), chart_rect)

    count = len(fitness_history)
    if count < 2:
        # Not enough data to draw a line
        draw_text("No fitness data", font, WHITE, screen, x_offset + width // 2, y_offset + height // 2)
        return

    # Find min and max to scale the data
    min_val = min(fitness_history)
    max_val = max(fitness_history)
    if min_val == max_val:
        max_val = min_val + 1  # Avoid div-by-zero

    # We'll plot the data across the width
    # x step: how many pixels per data point
    x_step = width / (count - 1)  # if we have count data points, we do count-1 segments

    # We invert y because top is smaller y
    def transform(i, val):
        """
        i = index, val = fitness
        Return (px, py) on the chart
        """
        px = x_offset + i * x_step
        # rescale val -> [0..1]
        fraction = (val - min_val) / (max_val - min_val)
        # invert so higher fitness is "higher" in chart area
        py = y_offset + height - fraction * height
        return (px, py)

    points = [transform(i, val) for i, val in enumerate(fitness_history)]

    # Draw lines between consecutive points
    for i in range(len(points) - 1):
        pygame.draw.line(screen, (200, 200, 50), points[i], points[i+1], 2)

    # Optionally draw the last fitness numeric
    last_val = fitness_history[-1]
    draw_text(f"Avg Fitness: {last_val:.1f}", font, WHITE, screen, x_offset + width // 2, y_offset + 20)

def game_loop(screen, clock, font_small, bg_img):
    global fitness_history

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

    died_chromosomes = []

    # Clear fitness_history each new game session
    fitness_history = []

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

        # Spawning
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            if len(died_chromosomes) >= 2 and random.random() < 0.7:
                parentA = random.choice(died_chromosomes)
                parentB = random.choice(died_chromosomes)
                child_chrom = EnemyChromosome.crossover(parentA, parentB)
                child_chrom.mutate(mutation_rate=0.15)
                enemy = Enemy(level, chromosome=child_chrom)
            else:
                enemy = Enemy(level)
            all_sprites.add(enemy)
            enemies.add(enemy)

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        # Check if enemies escaped
        for enemy in enemies.copy():
            if enemy.rect.top > SCREEN_HEIGHT:
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
            enemy.chromosome.add_fitness(-20)
            died_chromosomes.append(enemy.chromosome)

        # Enemy-player collisions
        collided_enemies = pygame.sprite.spritecollide(player, enemies, True)
        for enemy in collided_enemies:
            player.health -= 20
            enemy.chromosome.add_fitness(50)
            died_chromosomes.append(enemy.chromosome)

        # Drawing
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(BLACK)

        # Left side (0..SCREEN_WIDTH): the main game
        all_sprites.draw(screen)
        player.draw_health_bar(screen)

        draw_text(f"Score: {score}", font_small, WHITE, screen, 60, 20)
        draw_text(f"Level: {level}", font_small, WHITE, screen, SCREEN_WIDTH - 60, 20)
        draw_text(f"Escaped: {escaped_enemies}/{max_escaped}", font_small, WHITE, screen, SCREEN_WIDTH // 2, 20)

        # ==============================
        # == Right side: charts & stats
        # ==============================
        chart_x = SCREEN_WIDTH
        chart_y = 0
        chart_w = TOTAL_WIDTH - SCREEN_WIDTH
        chart_h = SCREEN_HEIGHT

        # Top half for gene stats
        half_h = chart_h // 2
        all_chromosomes = [enemy.chromosome for enemy in enemies] + died_chromosomes
        draw_chromosome_stats(screen, chart_x, chart_y, chart_w, half_h, font_small, all_chromosomes)

        # Bottom half for fitness chart
        # 1) Calculate average fitness from all chromosomes
        if all_chromosomes:
            avg_fitness = sum(c.fitness for c in all_chromosomes) / len(all_chromosomes)
        else:
            avg_fitness = 0.0
        # 2) Append to the history
        fitness_history.append(avg_fitness)
        # 3) Draw the line chart
        draw_fitness_chart(screen, chart_x, chart_y + half_h, chart_w, half_h, font_small)

        pygame.display.flip()
