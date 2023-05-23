from functools import cached_property
from global_settings import TILE_SIZE
import pygame
from pygame import Vector2


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos: Vector2, screen_pos_ref: list[float, float]):
        super().__init__()
        self.pos = pos + Vector2(TILE_SIZE/2, TILE_SIZE/2)
        self.screen_pos_ref = screen_pos_ref
        self.rotation_counter = 0
        self.bounce_counter = 0
        self.animation_state = 0

    FRAMES_PER_ANIMATION_STATE = 15
    N_ANIMATION_STATES = 8
    FRAMES_PER_ROTATION = 120
    FRAMES_PER_BOUNCE = 150
    RECTS = ((0, 0, 64, 64),
             (68, 0, 56, 64),
             (128, 0, 48, 64),
             (180, 0, 36, 64),
             (220, 0, 20, 64),
             (0, 68, 36, 64),
             (40, 68, 48, 64),
             (92, 68, 56, 64))

    @property
    def rect(self):
        return self.image.get_rect(center=(self.pos.x - self.screen_pos_ref[0],
                                           self.pos.y - self.screen_pos_ref[1]))

    @property
    def image(self) -> pygame.Surface:
        return self.all_images[self.animation_state]

    def update(self):
        # pos
        self.bounce_counter += 1
        if self.bounce_counter >= self.FRAMES_PER_BOUNCE:
            self.bounce_counter -= self.FRAMES_PER_BOUNCE
        self.pos.y += (self.bounce_counter - ((self.FRAMES_PER_BOUNCE - 1) / 2)) / 44
        # animation
        self.rotation_counter += 1
        if self.rotation_counter >= self.FRAMES_PER_ROTATION:
            self.rotation_counter -= self.FRAMES_PER_ROTATION
        self.animation_state = self.rotation_counter // self.FRAMES_PER_ANIMATION_STATE

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    @cached_property
    def all_images(self):
        image = pygame.image.load(r"..\textures\coins 3.png").convert()
        image.set_colorkey((0, 0, 0))
        image = pygame.transform.scale_by(image, 4)
        return tuple(image.subsurface(rect) for rect in self.RECTS)
