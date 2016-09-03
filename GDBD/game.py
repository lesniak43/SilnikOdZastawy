from weakref import ref, proxy

import numpy as np
import pygame

from zastawa.engine import *

FPS = 60

s = SceneHex(0)

N = 150
s.TIMEOUT = 15
s.MAX_PER_HEX = 1

v = HexView(s)
for uid in xrange(N):
    x = np.random.randint(-50, 50)
    y = np.random.randint(-50, 50)
    x = 0
    y = 0
    z = - (x + y)
    color = (np.random.randint(256), np.random.randint(256), np.random.randint(256))
    s.items.append(HexItem(uid, hex_position=np.array((x,y,z)), speed=np.random.randint(1, 11), color=color))

clock = pygame.time.Clock()
screen = pygame.display.set_mode((800,600))



def main():
    while True:
        s.tick()
        v.draw_scene(screen)
        pygame.display.flip()
        clock.tick(FPS)

main()
