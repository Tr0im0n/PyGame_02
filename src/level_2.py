import math
from collections import deque
from functools import cached_property
import random

import numpy as np
import pygame.sprite
from pygame import Vector2

from coin import Coin
from global_settings import *
from player_sprite import PlayerSprite
from shape_groups import CircleGroup, FireflyGroup
from shapes import CircleParticle, FireflyParticle
from text_sprite import TextSprite


class Level:
    """
    pos_screen: top left coord of screen
    pos_player: pos of player on screen
    loaded_chunks: dict of chunks keys is chunk pos tuple e.g. {(1,2): chunk3}

    Scroll:
    player moves one screen --> changes pos_player
    change pos_screen based on pos_player offset from middle of screen

    Draw:
    Lets write these functions, so we can adapt the chunk class to those needs.
    Layers: Groups?
    0: background, no scroll
    1. parallax layer: 0.25 scroll
    2. parallax layer: 0.5 scroll
    3. parallax layer: 0.75 scroll
    4. tiles: 1 scroll
    10. collision: 1 scroll
    11. shrubs?: 1 scroll
    20. particles: 1.1 scroll

    How to detect particle moving from one chunk to another
    """
    def __init__(self):
        self.file_name = "level_map_2.txt"
        self.map = []
        self.chunks = {}
        self.used_layers = [4, 10, 11, 20, 21]
        self.screen_pos = [1300, 1500]
        self.scroll_delay = (32, 24)
        self.player_group = pygame.sprite.GroupSingle(PlayerSprite(self.screen_pos))
        self.coins = 0

    def load_map_from_txt(self) -> None:
        with open(self.file_name) as file:
            self.map = tuple(line for line in file)

    def load_chunk(self, chunk_key: tuple[int, int]) -> None:
        new_chunk = {}
        tile_pos = (0, 0)
        for tile_x in range(CHUNK_SIZE):
            for tile_y in range(CHUNK_SIZE):
                char_pos = (chunk_key[0]*CHUNK_SIZE+tile_x, chunk_key[1]*CHUNK_SIZE+tile_y)
                char = self.map[char_pos[1]][char_pos[0]]
                if char == "A":
                    if not random.randrange(100):
                        if 21 not in new_chunk:
                            new_chunk[21] = FireflyGroup()
                        new_firefly = FireflyParticle(Vector2(tile_pos))
                        new_chunk[21].add(new_firefly)
                tile_pos = (char_pos[0]*TILE_SIZE, char_pos[1]*TILE_SIZE)
                if char == "D":
                    if 4 not in new_chunk:
                        new_chunk[4] = pygame.sprite.Group()
                    new_dirt = Tile(self.dirt_surf, tile_pos, self.screen_pos)
                    new_chunk[4].add(new_dirt)
                elif char == "G":
                    if 10 not in new_chunk:
                        new_chunk[10] = pygame.sprite.Group()
                    new_grass = Tile(self.grass_surf, tile_pos, self.screen_pos)
                    new_chunk[10].add(new_grass)
                elif char == "C":
                    if 11 not in new_chunk:
                        new_chunk[11] = pygame.sprite.Group()
                    new_coin = Coin(Vector2(tile_pos), self.screen_pos)
                    new_chunk[11].add(new_coin)

        self.chunks[chunk_key] = new_chunk
        return

    def unload_chunk(self, chunk_key):
        # this might need some saving mechanic
        # for things that have been interacted with
        self.chunks.pop(chunk_key)

    def chunks_on_screen(self) -> tuple:
        # these int() shouldn't ben necessary as screen_pos now always is an int
        x_min = int(self.screen_pos[0])//CHUNK_RES
        x_max = (int(self.screen_pos[0])+SCREEN_WIDTH)//CHUNK_RES + 1
        y_min = int(self.screen_pos[1]) // CHUNK_RES
        y_max = (int(self.screen_pos[1]) + SCREEN_HEIGHT) // CHUNK_RES + 1
        return tuple((x, y) for x in range(x_min, x_max) for y in range(y_min, y_max))

    def player_chunk(self) -> tuple:
        px = int(self.player_group.sprite.rect.centerx + self.screen_pos[0]) // CHUNK_RES
        py = int(self.player_group.sprite.rect.centery + self.screen_pos[1]) // CHUNK_RES
        return px, py

    def chunks_around_player(self) -> tuple:
        px, py = self.player_chunk()
        return tuple((x, y) for x in range(px-1, px+2) for y in range(py-1, py+2) if (x, y) in self.chunks)

    def update(self) -> None:
        chunks_on_screen = self.chunks_on_screen()
        # chunk unloading
        unload_list = []
        for chunk_key in self.chunks:
            if chunk_key not in chunks_on_screen:
                unload_list.append(chunk_key)
        for chunk_key in unload_list:
            self.unload_chunk(chunk_key)

        for chunk_key in self.chunks_on_screen():
            # chunk loading
            if chunk_key not in self.chunks:
                self.load_chunk(chunk_key)
            # updating
            for layer in (11, 20, 21):
                if layer in self.chunks[chunk_key]:
                    self.chunks[chunk_key][layer].update()
        # player update
        self.player_group.update()
        self.update_player_pos_scroll_and_check_collisions()
        self.check_coin_collision()

    def draw(self, screen: pygame.Surface) -> None:
        for layer in self.used_layers:
            for key in self.chunks:
                if layer not in self.chunks[key]:
                    continue
                if layer in (20, 21):
                    self.chunks[key][layer].draw(screen, self.screen_pos)
                else:
                    self.chunks[key][layer].draw(screen)
            if layer == 10:
                self.player_group.draw(screen)
        # todo fix this garbage
        pygame.sprite.Group(TextSprite(f"coins: {self.coins}", Vector2(200, 100))).draw(screen)

    def jump(self):
        self.player_group.sprite.jump()

    def update_player_pos_scroll_and_check_collisions(self):
        # qol
        player = self.player_group.sprite
        # x scroll
        x_scroll = (self.player_group.sprite.pos.x - (SCREEN_WIDTH/2) - self.screen_pos[0]) / self.scroll_delay[0]
        self.screen_pos[0] += x_scroll
        # x movement
        self.player_group.sprite.pos.x += player.vel.x
        # x collision
        if x_collision_sprite_list := self.player_collisions_with_layer(10):
            player.vel.x = 0
            for sprite in x_collision_sprite_list:
                if player.facing_east:
                    player.pos.x = -0.5 * player.rect.width + sprite.rect.left + self.screen_pos[0]
                else:
                    player.pos.x = 0.5 * player.rect.width + sprite.rect.right + self.screen_pos[0]
        # y scroll
        y_scroll = (self.player_group.sprite.pos.y - (SCREEN_HEIGHT / 2) - self.screen_pos[1]) / self.scroll_delay[1]
        self.screen_pos[1] += y_scroll
        # y movement
        self.player_group.sprite.pos.y += player.vel.y
        # y collision
        player.on_ground = False
        if y_collision_sprite_list := self.player_collisions_with_layer(10):
            # dust particles
            n_particles = max(0, round(player.vel.y-2))
            if abs(player.vel.x) > 4:
                n_particles += 1
            # back to collisions
            player.vel.y = 0
            for sprite in y_collision_sprite_list:
                if player.facing_down:
                    player.pos.y = -0.5 * player.rect.height + sprite.rect.top + self.screen_pos[1]
                    player.stamina = 1
                    player.on_ground = True
                    self.add_circle_particle(player.rect.midbottom, n_particles)
                else:
                    player.pos.y = 0.5 * player.rect.height + sprite.rect.bottom + self.screen_pos[1]

    def player_collisions_with_layer(self, layer: int, dokill: bool = False) -> list:
        player = self.player_group.sprite
        collision_sprite_list = []
        for chunk_key in self.chunks_around_player():
            if layer in self.chunks[chunk_key]:
                collisions = pygame.sprite.spritecollide(player, self.chunks[chunk_key][layer], dokill)
                for collision in collisions:
                    collision_sprite_list.append(collision)
        return collision_sprite_list

    def check_coin_collision(self):
        if coin_collisions := self.player_collisions_with_layer(11, True):
            player_chunk = self.player_chunk()
            if 20 not in self.chunks[player_chunk]:
                self.chunks[player_chunk][20] = CircleGroup()
            n_particles = 16
            for coin in coin_collisions:
                self.coins += 1
                for i in range(n_particles):
                    new_circle = CircleParticle(Vector2(coin.pos.x, coin.pos.y),
                                                radius=16,
                                                radius_decay=0.5,
                                                color=(255, 175, 0))
                    self.chunks[player_chunk][20].add(new_circle)

    def add_circle_particle(self, pos: Vector2, n_particles: int = 1) -> None:
        player_chunk = self.player_chunk()
        if 20 not in self.chunks[player_chunk]:
            self.chunks[player_chunk][20] = CircleGroup()
        for i in range(n_particles):
            ans = random.uniform(-1, 1)
            angle = math.sqrt(ans) if ans >= 0 else -math.sqrt(-ans)
            angle -= 1
            angle *= 90
            new_circle = CircleParticle(pos + Vector2(self.screen_pos), angle_range=(angle, angle))
            self.chunks[player_chunk][20].add(new_circle)

    # Textures -------------------------------------------------------------------------------------

    @cached_property
    def dirt_surf(self):
        ans = pygame.image.load(r"../textures/dirt.png").convert()
        return pygame.transform.scale_by(ans, 4)

    @cached_property
    def grass_surf(self):
        ans = pygame.image.load(r"../textures/grass_block_side.png").convert()
        return pygame.transform.scale_by(ans, 4)


class Tile(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, pos: tuple[int, int], screen_pos_ref: list[float, float]):
        super().__init__()
        self.screen_pos_ref = screen_pos_ref
        self.image = image
        self.pos = pos

    @property
    def rect(self):
        return self.image.get_rect(topleft=(self.pos[0]-self.screen_pos_ref[0], self.pos[1]-self.screen_pos_ref[1]))
