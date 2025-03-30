import pygame
import random
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GREEN, RED, PLAYER_SPRITE, ENEMY_SPRITES

class EnemyChromosome:
    """
    A container for enemy 'genes' plus logic for mutation, crossover, fitness, etc.
    """
    def __init__(
        self,
        speed_gene=None,
        health_gene=None,
        bullet_speed_gene=None,
        sprite_scale_gene=None,
        color_tint_gene=None
    ):
        """
        Randomly initialize each gene if it's not provided.
        
        For example:
        - speed_gene: [1..5]
        - health_gene: [1..3] (multiplier for base health)
        - bullet_speed_gene: [5..12]
        - sprite_scale_gene: [50..150]  (percentage scale)
        - color_tint_gene: [0..255]    (simple color overlay value)
        """
        self.speed_gene = speed_gene if speed_gene is not None else random.randint(1, 5)
        self.health_gene = health_gene if health_gene is not None else random.randint(1, 3)
        self.bullet_speed_gene = bullet_speed_gene if bullet_speed_gene is not None else random.randint(5, 12)
        self.sprite_scale_gene = sprite_scale_gene if sprite_scale_gene is not None else random.randint(50, 150)
        self.color_tint_gene = color_tint_gene if color_tint_gene is not None else random.randint(0, 255)

        # Track how "successful" or "fit" the enemy was
        self.fitness = 0

    def mutate(self, mutation_rate=0.1):
        """
        Example mutation: with some probability, each gene is tweaked slightly.
        """
        if random.random() < mutation_rate:
            self.speed_gene = max(1, self.speed_gene + random.choice([-1, 1]))
        if random.random() < mutation_rate:
            self.health_gene = max(1, self.health_gene + random.choice([-1, 1]))
        if random.random() < mutation_rate:
            self.bullet_speed_gene = max(1, self.bullet_speed_gene + random.choice([-2, -1, 1, 2]))
        if random.random() < mutation_rate:
            # sprite_scale_gene in [10..200] to avoid extremes
            self.sprite_scale_gene = max(10, min(200, self.sprite_scale_gene + random.choice([-10, -5, 5, 10])))
        if random.random() < mutation_rate:
            # color_tint_gene in [0..255]
            shift = random.randint(-30, 30)
            self.color_tint_gene = min(255, max(0, self.color_tint_gene + shift))

    @staticmethod
    def crossover(parentA, parentB):
        """
        Simple uniform crossover:
        For each gene, pick from either parent with 50% chance.
        """
        child = EnemyChromosome(
            speed_gene = parentA.speed_gene if random.random() < 0.5 else parentB.speed_gene,
            health_gene = parentA.health_gene if random.random() < 0.5 else parentB.health_gene,
            bullet_speed_gene = parentA.bullet_speed_gene if random.random() < 0.5 else parentB.bullet_speed_gene,
            sprite_scale_gene = parentA.sprite_scale_gene if random.random() < 0.5 else parentB.sprite_scale_gene,
            color_tint_gene = parentA.color_tint_gene if random.random() < 0.5 else parentB.color_tint_gene
        )
        return child

    def add_fitness(self, amount):
        """Add a certain amount to this chromosome's fitness."""
        self.fitness += amount

    def __repr__(self):
        return (f"<EnemyChromosome speed={self.speed_gene} "
                f"health={self.health_gene} bullet_speed={self.bullet_speed_gene} "
                f"scale={self.sprite_scale_gene} color={self.color_tint_gene} "
                f"fitness={self.fitness}>")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(PLAYER_SPRITE).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 7
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
        # Draw the bar above the player so it’s visible:
        outline_rect = pygame.Rect(self.rect.centerx - bar_length // 2, self.rect.top - 20, bar_length, bar_height)
        fill_rect = pygame.Rect(self.rect.centerx - bar_length // 2, self.rect.top - 20, fill, bar_height)
        pygame.draw.rect(surface, RED, outline_rect)
        pygame.draw.rect(surface, GREEN, fill_rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level, chromosome=None):
        super().__init__()
        sprite_index = random.randint(0, len(ENEMY_SPRITES) - 1)
        self.image = pygame.image.load(ENEMY_SPRITES[sprite_index]).convert_alpha()

        # Assign or create a chromosome
        if chromosome is None:
            self.chromosome = EnemyChromosome()
        else:
            self.chromosome = chromosome

        # Scale the sprite according to sprite_scale_gene
        scale_percent = self.chromosome.sprite_scale_gene
        width = self.image.get_width() * scale_percent // 100
        height = self.image.get_height() * scale_percent // 100
        self.image = pygame.transform.scale(self.image, (width, height))

        # Optionally tint the sprite with color_tint_gene
        # This example adds a tinted overlay (primarily red).
        tint_surf = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        # color_tint_gene -> interpret as some intensity in the red channel
        tint_surf.fill((self.chromosome.color_tint_gene, 0, 0, 50))
        self.image.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, SCREEN_WIDTH - 50 - self.rect.width)
        self.rect.y = random.randint(-100, -40)

        # Combine chromosome speed with the level
        self.speed = self.chromosome.speed_gene + level

        # For health, we can start with base 20, multiplied by health_gene
        self.health = 20 * self.chromosome.health_gene

    def update(self):
        self.rect.y += self.speed

        # Award some "travel fitness" for each update tick it stays alive
        self.chromosome.add_fitness(self.speed)

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
