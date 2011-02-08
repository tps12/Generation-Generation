import noise

import pygame
from pygame import display, draw, event, Surface
from pygame.locals import *
from pygame.sprite import Sprite, Group
from pygame.time import Clock

def grayvalue(v):
    return [int(128 * v) for i in range(3)]

pygame.init()

screen = display.set_mode((800,800), HWSURFACE)
display.set_caption('Generations')

def noiseat(x, y):
    return 1 + noise.snoise2(
            x/10.0,
            y/800.0,
            24,
            1)

def sex(x, y):
    return noise.snoise2((x+6253),(y-1220),1,1) > 0
           
background = Surface(screen.get_size())
background.lock()
for y in range(0, background.get_height()):
    for x in range(0, background.get_width()):
        background.set_at((x,y), grayvalue(noiseat(x,y)))
background.unlock()

screen.blit(background, (0,0))

sprites = Group()

def personat(x,y):
    return noiseat(x*8,y*8) <= 0.95

for x in range(0, background.get_width(), 8):
    for y in range(0, background.get_height(), 8):
        if not personat(x/8, y/8):
            continue
        
        sprite = Sprite()
        sprite.image = Surface((4,4), flags=SRCALPHA)
        male = sex(x,y)
        draw.circle(sprite.image, (196,196,255) if male else (255,196,196),
                    (2,2), 2, 1)
        sprite.rect = sprite.image.get_rect().move(x, y)
        sprites.add(sprite)

limit = Clock()

done = False

while not done:
    for e in event.get():
        if e.type == QUIT:
            done = True
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                done = True
        elif e.type == MOUSEBUTTONDOWN and e.button == 1:
            for sprite in sprites:
                if sprite.rect.collidepoint(e.pos):
                    generation = sprite.rect.left / 8
                    index = sprite.rect.top / 8

                    if generation > 0:
                        family = 0
                        infam = False
                        for i in range(0, index):
                            if personat(generation, i):
                                if not infam:
                                    infam = True
                            else:
                                if infam:
                                    infam = False
                                    family += 1
                        print family
                    
                    break

    sprites.update()
    sprites.clear(screen, background)
    sprites.draw(screen)
    
    display.flip()

    limit.tick(20)
