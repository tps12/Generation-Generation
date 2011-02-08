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
        male = sex(x/8,y/8)
        draw.circle(sprite.image, (196,196,255) if male else (255,196,196),
                    (2,2), 2, 1)
        sprite.rect = sprite.image.get_rect().move(x, y)
        sprites.add(sprite)

limit = Clock()

done = False

def family(generation, index):
    fam = 0
    infam = False
    for i in range(0, index):
        if personat(generation, i):
            if not infam:
                infam = True
        else:
            if infam:
                infam = False
                fam += 1
    return fam

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
                        fam = family(generation, index)

                        i = 0
                        mom = dad = None
                        men = women = 0
                        while True:
                            if personat(generation-1, i):                                    
                                pfam = family(generation-1, i)

                                if mom is None and dad is None:
                                    if sex(generation-1, i):
                                        if men >= fam:
                                            dad = i, pfam
                                        else:
                                            men += 1
                                    else:
                                        if women >= fam:
                                            mom = i, pfam
                                        else:
                                            women += 1
                                elif mom is not None:
                                    if sex(generation-1, i):
                                        if men >= fam:
                                            if pfam != mom[1]:
                                                dad = i, pfam
                                                break
                                        else:
                                            men += 1
                                else:
                                    if not sex(generation-1, i):
                                        if women >= fam:
                                            if pfam != dad[1]:
                                                mom = i, pfam
                                                break
                                        else:
                                            women += 1
                            i += 1

                        print mom[0], dad[0]
                    break

    sprites.update()
    sprites.clear(screen, background)
    sprites.draw(screen)
    
    display.flip()

    limit.tick(20)
