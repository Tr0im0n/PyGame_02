from abc import ABC
from collections import deque
import pygame
from shapes import AbstractShapeSprite


class AbstractShapeGroup(ABC):
    def __init__(self):
        self.particle_queue = deque()

    def add(self, shape: AbstractShapeSprite):
        self.particle_queue.append(shape)

    def update(self):
        for particle in self.particle_queue:
            particle.update()

    def draw(self, screen: pygame.Surface, screen_pos: list[float, float]) -> None:
        for particle in self.particle_queue:
            particle.draw(screen, screen_pos)


class CircleGroup(AbstractShapeGroup):

    def update(self):
        for particle in self.particle_queue:
            particle.update()
        # pop condition
        while self.particle_queue:
            if self.particle_queue[0].radius <= 0:
                self.particle_queue.popleft()
            else:
                break


class FireflyGroup(AbstractShapeGroup):
    pass
