import numpy as np
import pygame

from global_settings import SCREEN_WIDTH, SCREEN_HEIGHT


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, screen_pos_ref: list[float, float]):
        super().__init__()
        texture_file_name = "bricks.png"
        image = pygame.image.load(r"../textures/" + texture_file_name).convert()
        self.image = pygame.transform.scale_by(image, 4)
        self.screen_pos_ref = screen_pos_ref

        self.pos = pygame.math.Vector2(SCREEN_WIDTH/2 + screen_pos_ref[0], SCREEN_HEIGHT/2 + screen_pos_ref[1])
        self.vel = pygame.math.Vector2(0, 0)
        self.gravity = 1
        self.friction = 1
        self.air_res = pygame.math.Vector2(100, 300)
        self.acc = pygame.math.Vector2(2, 1)
        self.jump_acc = -28
        self.stamina = 1
        self.facing_east = True
        self.facing_down = True
        self.on_ground = False
        self.jump_buffer = 0

    @property
    def rect(self):
        return self.image.get_rect(center=(round(self.pos.x) - self.screen_pos_ref[0],
                                           round(self.pos.y) - self.screen_pos_ref[1]))

    def jump(self):
        if self.stamina > 0:
            self.vel.y = self.jump_acc
            if not self.on_ground:
                self.stamina -= 1
        elif not self.on_ground:
            self.jump_buffer = 2

    def update(self) -> None:
        # jump buffer
        if self.jump_buffer:
            if self.on_ground:
                self.jump()
            self.jump_buffer -= 1
        # handling WASD
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_a]:
            self.vel.x -= self.acc.x
        if pressed_keys[pygame.K_d]:
            self.vel.x += self.acc.x
        if pressed_keys[pygame.K_s]:
            self.vel.y += self.acc.y
        # changes velocity
        self.vel.y += self.gravity
        # air resistence
        if self.vel.x:
            self.vel.x *= 1 - np.tanh(abs(self.vel.x)/self.air_res.x)
        if self.vel.y:
            self.vel.y *= 1 - np.tanh(abs(self.vel.y)/self.air_res.y)
        # surface friction
        if abs(self.vel.x) <= self.friction:
            self.vel.x = 0
        elif self.vel.x > 0:
            self.vel.x -= self.friction
        else:
            self.vel.x += self.friction
        # facing east or west
        if self.facing_east:
            if self.vel.x < 0:
                self.facing_east = False
        else:
            if self.vel.x > 0:
                self.facing_east = True
        # facing down or up
        if self.facing_down:
            if self.vel.y < 0:
                self.facing_down = False
        else:
            if self.vel.y > 0:
                self.facing_down = True
