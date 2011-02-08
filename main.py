import noise

import pygame
from pygame import display, event, Surface
from pygame.locals import *
from pygame.sprite import Sprite, Group
from pygame.time import Clock

def gray_value(v):
    return [int(128 * (1 + v)) for i in range(3)]

pygame.init()

screen = display.set_mode((800,600), HWSURFACE)
display.set_caption('Generations')

background = Surface(screen.get_size())
background.lock()
for y in range(0, background.get_height()):
    for x in range(0, background.get_width()):
        background.set_at((x,y), gray_value(noise.snoise2(
            (x+50) / 600.0 / 512,
            (y-900) / 600.0 / 512,
            12,
            1)))
background.unlock()

screen.blit(background, (0,0))

sprites = Group()

limit = Clock()

done = False

while not done:
    for e in event.get():
        if e.type == QUIT:
            done = True
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                done = True

    sprites.update()
    sprites.clear(screen, background)
    sprites.draw(screen)
    
    display.flip()

    limit.tick()
