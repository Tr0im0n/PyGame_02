
import pygame
from pygame import Vector2

from global_settings import *
import level_2
from text_sprite import TextSprite

# Init ########################################################################
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("IS THAT AMOGUS???")
clock = pygame.time.Clock()
start_time = 0
in_menu = False

# Groups #########################################################################
level2 = level_2.Level()
level2.load_map_from_txt()

# Timer #########################################################################
timer_2s = pygame.USEREVENT + 1
pygame.time.set_timer(timer_2s, 2000)

# Loop ###########################################################################
run = True
while run:
    # user inputs
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                in_menu = not in_menu
            if event.key == pygame.K_SPACE:
                level2.jump()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
        if event.type == pygame.MOUSEBUTTONUP:
            pass
        if event.type == timer_2s:
            pass

    # static blits #########################################################################
    screen.fill((0, 0, 15))

    # moving blits ########################################################################
    level2.update()
    level2.draw(screen)

    # test ########################################################################

    # end ########################################################################
    pygame.display.update()
    # print(clock.get_fps())
    clock.tick(FPS)

pygame.quit()
