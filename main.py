from collections import deque
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

dx = randint(-2048,2048)
dy = randint(-2048,2048)
def noiseat(x, y):
    global dx
    global dy
    return 1 + noise.snoise2(
            (x+dx)/10.0,
            (y+dy)/800.0,
            24,
            1)

sdx = randint(-2048,2048)
sdy = randint(-2048,2048)
def sex(x, y):
    global sdx
    global sdy
    return noise.snoise2((x+sdx),(y+sdy),1,1) > 0

cdx = randint(-2048,2048)
cdy = randint(-2048,2048)
def childless(x, y):
    global cdx
    global cdy
    return noise.snoise2((x+cdx),(y+cdy),1,1) > 0.5

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

def people(generation):
    fam = 0
    infam = False
    i = 0
    while True:
        if personat(generation, i):
            yield i, fam
            if not infam:
                infam = True
        else:
            if infam:
                infam = False
                fam += 1
        i += 1

def members(generation, family):
    for i, fam in people(generation):
        if fam == family:
            yield i
        elif fam > family:
            return

def couples(generation):
    men = deque()
    women = deque()

    ps = people(generation)
    while True:
        i, fam = next(ps)
        if childless(generation, i):
            continue
        if sex(generation, i):
            if women and women[0][1] != fam:
                yield women.popleft()[0], i
            else:
                men.append((i,fam))
        else:
            if men and men[0][1] != fam:
                yield i, men.popleft()[0]
            else:
                women.append((i,fam))
    
def couple(generation, n):
    cs = couples(generation)
    while True:
        c = next(cs)
        if not n:
            return c
        n -= 1

def spouse(generation, index):
    cs = couples(generation)
    n = 0
    while True:
        c = next(cs)
        if index in c:
            return (n, c[0] if c[1] == index else c[1])
        n += 1

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

    if childless(generation, index):
        print 'childless'
    else:
        n, partner = spouse(generation, index)
        print 'spouse',partner

        kids = members(generation+1, n)
        print 'kids',', '.join([str(k) for k in kids])

    gen = generation - 1
    fathers = []
    while gen >= 0 and len(fathers) < 10:
        fore = couple(gen, fam)[1]
        fam = family(gen, fore)
        fathers.append(fore)
        gen -= 1
    print fathers

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
                index = randint(0,100000)
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
