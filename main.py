from random import randint
from sys import argv

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

shownoise = '-shownoise' in [a.lower() for a in argv]
           
background = Surface(screen.get_size())
if shownoise:
    background.lock()
    for y in range(0, background.get_height()):
        for x in range(0, background.get_width()):
            background.set_at((x,y), grayvalue(noiseat(x,y)))
    background.unlock()
else:
    background.fill((255,255,255))

screen.blit(background, (0,0))

sprites = Group()

def personat(x,y):
    return noiseat(x*8,y*8) <= 0.95

for x in range(0, background.get_width(), 8):
    for y in range(0, background.get_height(), 8):
        present = personat(x/8, y/8)
        if shownoise and not present:
            continue
        
        sprite = Sprite()
        sprite.image = Surface((4,4), flags=SRCALPHA)
        if present:
            sprite.exists = True
            male = sex(x/8,y/8)
            draw.circle(sprite.image, (196,196,255) if male else (255,196,196),
                            (2,2), 2, 1 if shownoise else 0)
        else:
            sprite.exists = False
        if not shownoise:
            draw.circle(sprite.image, (128,128,128), (2,2), 2, 1)
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

def members(generation, family):
    fam = 0
    infam = False
    i = 0
    sibs = []
    while True:
        if personat(generation, i):
            if not infam:
                infam = True
            if fam == family:
                sibs.append(i)
        else:
            if infam:
                infam = False
                if fam == family:
                    break
                fam += 1
        i += 1
    return sibs

def couples(generation):
    n = 0
    while True:
        i = 0
        mom = dad = None
        men = women = 0
        while True:
            if personat(generation, i):                                    
                pfam = family(generation, i)

                if mom is None and dad is None:
                    if sex(generation, i):
                        if men >= n:
                            dad = i, pfam
                        else:
                            men += 1
                    else:
                        if women >= n:
                            mom = i, pfam
                        else:
                            women += 1
                elif mom is not None:
                    if sex(generation, i):
                        if men >= n:
                            if pfam != mom[1]:
                                dad = i, pfam
                                break
                        else:
                            men += 1
                else:
                    if not sex(generation, i):
                        if women >= n:
                            if pfam != dad[1]:
                                mom = i, pfam
                                break
                        else:
                            women += 1
            i += 1
        yield mom[0], dad[0]
        n += 1

def couple(generation, n):
    cs = couples(generation)
    while True:
        c = next(cs)
        if not n:
            return c
        n -= 1

def spouse(generation, index):
    i = 0
    while True:
        pair = couple(generation, i)
        if index in pair:
            return pair[0] if pair[1] == index else pair[1]
        i += 1

def children(generation, index):
    i = 0
    while True:
        kids = members(generation+1, i)
        if index in couple(generation, i):
            return kids
        i += 1

def describeperson(generation, index):
    print 'person',index

    fam = family(generation, index)
    print 'member of family',fam,'in generation', generation

    sibs = [m for m in members(generation, fam) if m != index]
    if sibs:
        print 'siblings', ', '.join([str(s) for s in sibs])
    else:
        print 'no siblings'

    if generation > 0:
        mom, dad = couple(generation-1, fam)
        print 'parents',mom,'and',dad

    partner = spouse(generation, index)
    print 'spouse',partner

    kids = children(generation, index)
    print 'kids',', '.join([str(k) for k in kids])

    print

while not done:
    for e in event.get():
        if e.type == QUIT:
            done = True
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                done = True
            elif e.unicode == u'r':
                generation = randint(0,500)
                index = randint(0,1000)
                while not personat(generation, index):
                    index += 1
                describeperson(generation, index)
                
        elif e.type == MOUSEBUTTONDOWN and e.button == 1:
            for sprite in sprites:
                if sprite.rect.collidepoint(e.pos) and sprite.exists:
                    generation = sprite.rect.left / 8
                    index = sprite.rect.top / 8

                    describeperson(generation, index)
                    
                    break

    sprites.update()
    sprites.clear(screen, background)
    sprites.draw(screen)
    
    display.flip()

    limit.tick(20)
