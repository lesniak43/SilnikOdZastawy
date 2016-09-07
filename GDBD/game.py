from weakref import ref, proxy

import numpy as np
import pygame

from zastawa.engine import *

FPS = 60

s = SceneHex(0)

N = 200
s.TIMEOUT = 1000000
s.MAX_PER_HEX = 1

v = HexView(s)
for uid in xrange(N):
    hex_position = \
        np.random.randint(-10, 10) * np.array((0, 1, -1)) + \
        np.random.randint(-10, 10) * np.array((-1, 1, 0)) + \
        np.random.randint(-10, 10) * np.array((-1, 0, 1))
    color = (np.random.randint(256), np.random.randint(256), np.random.randint(256))
    speed = np.random.randint(3,10)
    steps_per_move = int(float(FPS) / float(speed))
    s.add_item(HexItem(uid, hex_position=hex_position, color=color, steps_per_move=steps_per_move))

clock = pygame.time.Clock()
screen = pygame.display.set_mode((800,600))



pos1 = None
pos2 = None

def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return 0
                elif event.key == pygame.K_LEFT:
                    v.offset += np.array((100,0))
                elif event.key == pygame.K_RIGHT:
                    v.offset -= np.array((100,0))
                elif event.key == pygame.K_UP:
                    v.offset += np.array((0,100))
                elif event.key == pygame.K_DOWN:
                    v.offset -= np.array((0,100))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos1 = event.pos
                elif event.button == 2:
                    s.add_obstacle(v.describe_hex(event.pos))
                elif event.button == 3:
                    s.set_targets(v.describe_hex(event.pos))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pos2 = event.pos
                s.active_items_indices = v.items_in_rect(pos1, pos2)
                print pos1, pos2
        s.tick()
        v.draw_scene(screen)
        pygame.display.flip()
        clock.tick(FPS)
main()
