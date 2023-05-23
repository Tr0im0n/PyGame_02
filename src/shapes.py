import random
from abc import ABC, abstractmethod

import numpy as np
from pygame.math import Vector2
import pygame.math


class AbstractShapeSprite(ABC):
    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface, screen_pos: list[float, float]) -> None:
        pass


class CircleParticle(AbstractShapeSprite):
    def __init__(self,
                 pos: Vector2,
                 radius: float = 8,
                 angle_range: tuple[float, float] = (0, 360),
                 speed: float = 2,
                 acc: Vector2 = Vector2(0, 0.01),
                 color: tuple = (255, 255, 255),
                 width: int = 0,
                 radius_decay: float = 0.1):
        self.pos = pos
        self.radius = radius
        self.vel = Vector2.from_polar((speed, random.uniform(*angle_range)))
        self.acc = acc
        self.color = color
        self.width = width
        self.radius_decay = radius_decay

    def update(self) -> None:
        # termination has to be done somewhere else
        self.vel += self.acc
        self.pos += self.vel
        self.radius -= self.radius_decay

    def draw(self, screen: pygame.Surface, screen_pos: list[float, float]) -> None:
        pygame.draw.circle(screen, self.color, self.pos-Vector2(screen_pos), self.radius, self.width)


class RotatingSquareParticle(AbstractShapeSprite):
    # todo implement this
    def __init__(self,
                 pos: Vector2,
                 radius: float,
                 vel: Vector2 = Vector2(0, 0),
                 acc: Vector2 = Vector2(0, 0),
                 color: tuple = (0, 32, 64),
                 width: int = 16,
                 angle: int = 0,
                 angle_per_frame: float = 0.5):
        self.pos = pos
        self.radius = radius
        self.vel = vel
        self.acc = acc
        self.color = color
        self.width = width
        self.angle = angle
        self.angle_per_frame = angle_per_frame

    def update(self) -> None:
        self.vel += self.acc
        self.pos += self.vel
        self.angle += self.angle_per_frame

    def draw(self, screen: pygame.Surface) -> None:
        points = tuple((self.radius * np.cos((self.angle + i) * np.pi / 180) + self.pos.x,
                        self.radius * np.sin((self.angle + i) * np.pi / 180) + self.pos.y)
                       for i in (0, 90, 180, 270))
        pygame.draw.polygon(screen, self.color, points, self.width)


class KiteParticle(AbstractShapeSprite):
    def __init__(self,
                 pos: Vector2,
                 speed=4,
                 angle_range: tuple[int, int] = (0, 360),
                 color: tuple[int, int, int] = (255, 255, 255),
                 speed_decay=0.04):
        self.pos = Vector2(pos)
        self.speed = speed
        self.color = color
        self.speed_decay = speed_decay
        angle = random.uniform(*angle_range)
        self.point_angle = 30
        self.unit_vectors = tuple(Vector2.from_polar((1, angle+i)) for i in (0, self.point_angle, -self.point_angle))

    def update(self) -> None:
        self.speed -= self.speed_decay
        self.pos += self.speed * self.unit_vectors[0]

    def draw(self, screen: pygame.Surface) -> None:
        points = [8 * self.speed * self.unit_vectors[0] + self.pos,
                  2 * self.speed * self.unit_vectors[1] + self.pos,
                  -8 * self.speed * self.unit_vectors[0] + self.pos,
                  2 * self.speed * self.unit_vectors[2] + self.pos]
        pygame.draw.polygon(screen, self.color, points)


class FireflyParticle(AbstractShapeSprite):
    def __init__(self, pos: Vector2):
        self.pos = pos
        self.vel = Vector2(0, 0)
        self.circle_radius = 64
        self.square_radius = 4
        self.circle_color = 32, 16, 0
        self.square_color = 255, 191, 31
        self.acc_options = -0.01, 0, 0.01

    def update(self):
        # todo change this
        self.vel.x += random.choice(self.acc_options)
        self.vel.y += random.choice(self.acc_options)
        self.pos += self.vel

    def draw(self, screen: pygame.Surface, screen_pos_ref: list):
        surf = pygame.Surface((2*self.circle_radius, 2*self.circle_radius))
        pygame.draw.circle(surf, self.circle_color, (self.circle_radius, self.circle_radius), self.circle_radius)
        surf.set_colorkey((0, 0, 0))

        screen.blit(surf, (self.pos.x-self.circle_radius - screen_pos_ref[0],
                           self.pos.y-self.circle_radius - screen_pos_ref[1]),
                    special_flags=pygame.BLEND_RGB_ADD)
        pygame.draw.rect(screen, self.square_color, (self.pos.x - self.square_radius - screen_pos_ref[0],
                                                     self.pos.y - self.square_radius - screen_pos_ref[1],
                                                     2*self.square_radius, 2*self.square_radius))


class CrescentParticle(AbstractShapeSprite):

    def __init__(self, pos: Vector2):
        self.pos = pos
        self.radius1 = 192
        self.dr = 16
        self.radius2 = self.radius1 + self.dr
        self.max_width = 64
        self.dx = self.radius2 - self.radius1 + self.max_width

    def update(self):
        pass

    def draw(self, screen):
        # pos, dx, radius1, radius2
        surface = pygame.Surface((400, 400))
        pygame.draw.circle(surface, (255, 255, 255), (0, 200), self.radius1,
                           draw_top_right=True, draw_bottom_right=True)
        pygame.draw.circle(surface, (0, 0, 0), (-self.dx, 200), self.radius2,
                           draw_top_right=True, draw_bottom_right=True)
        surface.set_colorkey((0, 0, 0))
        screen.blit(surface, self.pos)

