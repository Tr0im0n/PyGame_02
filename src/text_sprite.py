import pygame


class TextSprite(pygame.sprite.Sprite):
    def __init__(self,
                 message: str,
                 pos: tuple[int, int],
                 color: tuple[int, int, int] = (127, 127, 127),
                 fade: bool = False,
                 font_name=None,
                 font_size: int = 50):
        super().__init__()
        self.fade = fade
        self.font = pygame.font.Font(font_name, font_size)
        self.image = self.font.render(message, False, color)
        if fade:
            self.image.set_alpha(254)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        if not self.fade:
            return
        new_alpha = self.image.get_alpha()
        if new_alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(new_alpha - 2)
            self.rect.move_ip(0, -1)


