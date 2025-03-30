# space_mutators_env.py

import pygame
import sys
import math
import random
import numpy as np
from pygame.locals import *
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from .sprite_defs import Player, Enemy, Bullet, EnemyChromosome

# Actions the agent can take
# We'll define a simple discrete action space:
# 0 -> do nothing
# 1 -> move left
# 2 -> move right
# 3 -> shoot

ACTIONS = {0: "NONE", 1: "LEFT", 2: "RIGHT", 3: "SHOOT"}

class SpaceMutatorsEnv:
    def __init__(self, render=False):

        self.render_mode = render
        self.clock = None
        self.screen = None

        # To handle no-render mode, we can optionally not create a visible display:
        if self.render_mode:
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.clock = pygame.time.Clock()
        else:
            # Headless:
            pygame.display.init()
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Basic environment settings
        self.spawn_interval = 60
        self.spawn_timer = 0
        self.level = 1
        self.max_levels = 3

        self._prev_player_x = None

        self.reset()

    def reset(self):

        # If we had multiple levels or waves, we'd reset them here
        self.score = 0
        self.escaped_enemies = 0
        self.max_escaped = 10

        # Pygame groups
        self.player = Player()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self._prev_player_x = self.player.rect.centerx
        self.done = False
        return self._get_observation()

        # Timer
        self.spawn_timer = 0

        # The agent's done condition
        self.done = False

        # Return the observation vector
        return self._get_observation()

    def _spawn_enemy(self):
        # We won't do genetic breeding here, just random enemies for now:
        enemy = Enemy(self.level, chromosome=EnemyChromosome())
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

    def step(self, action):

        # 1) Process action
        reward = 0.0
        self._handle_action(action)

        # 2) Spawn enemies periodically
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self._spawn_enemy()

        # 3) Update logic
        self._update()

        # 4) Calculate reward
        # We do some partial shaping:
        # - agent gets reward for shooting down enemies
        # - negative if the agent loses health
        # - negative if enemies escape
        # For more advanced shaping, see collisions logic in _update()
        reward += self._calculate_reward()

        # 5) Return next obs, reward, done, info
        obs = self._get_observation()
        return obs, reward, self.done, {}

    def _handle_action(self, action):

        if action == 1:  # left
            self.player.rect.x -= self.player.speed
        elif action == 2:  # right
            self.player.rect.x += self.player.speed
        elif action == 3:  # shoot
            bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)
        
        # Bound the player inside the screen
        if self.player.rect.x < 0:
            self.player.rect.x = 0
        if self.player.rect.right > SCREEN_WIDTH:
            self.player.rect.right = SCREEN_WIDTH

    def _update(self):

        # Update enemies and bullets
        self.enemies.update()
        self.bullets.update()

        # If an enemy goes off-screen at bottom:
        for enemy in self.enemies.copy():
            if enemy.rect.top > SCREEN_HEIGHT:
                self.escaped_enemies += 1
                enemy.kill()
                # We can check if that leads to done
                if self.escaped_enemies >= self.max_escaped:
                    self.done = True

        # Bullet-enemy collisions
        collisions = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for enemy in collisions.keys():
            self.score += 1
        
        # Enemy-player collisions
        collided_enemies = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for enemy in collided_enemies:
            self.player.health -= 20
            if self.player.health <= 0:
                self.done = True

        # Check leveling
        if self.score >= 20 * self.level and self.level < self.max_levels:
            self.level += 1
        if self.level > self.max_levels:
            # The player "wins" or we've passed the final wave
            self.done = True

        # Optionally do a render if in render_mode
        if self.render_mode:
            self._render()

    def _calculate_reward(self):
        reward = 0.0

        current_x = self.player.rect.centerx
        movement = abs(current_x - self._prev_player_x)

        # For each point in score, let's give +1 total
        # But we've already updated 'score' in _update, so we compare old vs new
        # For simplicity, let's do incremental reward at collisions time, or keep track of previous self.score

        #   +0.01 * (score) each step
        #   -0.01 each step (time penalty)
        #   -0.2 * escaped_enemies each step
        #   - if the player's health changed, we punish it
        # This is somewhat arbitrary, you'll want to refine.

        # Example:
        reward += 1.00 * self.score
        #reward -= 0.01
        reward -= 2.0 * self.escaped_enemies

        #Adding Reward on Movement
        #reward += 0.001 * movement


        #Prevent Standing Still
        if movement < 1:
            reward -= 1.0
        # If the player hasn't moved horizontally at all
        if movement > 2:
            reward += 0.5

        self._prev_player_x = current_x
        
        # If health < 100, let's penalize it
        # We won't track increments, but you could store old health in self._prev_health
        #reward -= (100 - self.player.health) * 0.001

        return reward

    def _render(self):

        self.screen.fill((0,0,0))
        self.all_sprites.draw(self.screen)
        # Could also draw the player's health bar if you like

        pygame.display.flip()
        self.clock.tick(FPS)

    def _get_observation(self):

        player_x = self.player.rect.centerx / float(SCREEN_WIDTH)
        player_health = self.player.health / 100.0

        # Just count # of enemies
        num_enemies = len(self.enemies)
        # maybe average enemy y
        avg_enemy_y = 0.0
        if num_enemies > 0:
            avg_enemy_y = sum(e.rect.centery for e in self.enemies) / (num_enemies * SCREEN_HEIGHT)
        # bullets
        num_bullets = len(self.bullets)

        obs = np.array([
            player_x, 
            player_health,
            num_enemies, 
            avg_enemy_y,
            num_bullets,
            self.score,
            self.escaped_enemies
        ], dtype=np.float32)

        return obs

    def close(self):
        if self.render_mode:
            pygame.quit()
