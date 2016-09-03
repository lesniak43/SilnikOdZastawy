from weakref import ref, proxy

import numpy as np
import pygame

from zastawa.engine import *
from data import WALLS, FLOORS, KEYBOARD1, FPS

pygame.init()

class Game(object):
# send high-level requests to worlds, displayer etc.
    def __init__(self, displayer, worlds):
        self.displayer = displayer
        self.worlds = worlds
        self.active_world = self.worlds[0]
        self.views = [] # rethink

    def add_view(self, view, layer, dest=(0, 0), shape=(800, 600)):
        self.displayer.add_view(proxy(view), layer, dest, shape)
        self.views.append(view)
        self.active_view = proxy(view)
        self.active_layer = layer

    def tick(self):
        pass
    def camera_move_right(self, dist):
        self.active_view.camera.move_right(dist)
    def camera_move_up(self, dist):
        self.active_view.camera.move_up(dist)
    def camera_move_forward(self, dist):
        self.active_view.camera.move_forward(dist)
    def camera_rotate_x(self, theta):
        self.active_view.camera.rotate_x(theta)
    def camera_rotate_y(self, theta):
        self.active_view.camera.rotate_y(theta)
    def camera_rotate_z(self, theta):
        self.active_view.camera.rotate_z(theta)
    def move_player(self, click_position, fps):
        view, coords = self.displayer.describe(click_position)
        self.active_view = view
        if view is not None:
            player = self.active_world.active_scene_.player_
            floor_plane = (0., 1., 0., 0.,)
            player_speed = 12.
            player.path_ = self.active_world.active_scene_.find_path(player.position_, view.describe(coords, floor_plane), speed=player_speed, fps=fps)
    def set_active_view(self, index):
        self.displayer.world.active_scene_.set_active_view(index)

"""
_perspective1 = Perspective(
    camera_position=np.array([0.,20.,50.]), camera_matrix=np.array([[0.,0.,-12.],[8.,0.,0.,],[0.,6.,0.,]]),
    screen_x=0, screen_y=0, screen_width=800, screen_height=600)
_perspective2 = Perspective(
    camera_position=np.array([0.,-20.,10.]), camera_matrix=np.array([[0.,0.,-12.],[8.,0.,0.,],[0.,6.,0.,]]),
    screen_x=0, screen_y=0, screen_width=800, screen_height=600)
_scene = Scene3D(id_=0, views=[_perspective0, _perspective2])
#_scene = Scene3D(id_=0, views=[_perspective1, _perspective2])
"""



_scene = Scene3D(id_=0)

_perspective0 = PerspectiveStereo(
    scene=_scene, camera_position=np.array([0.,20.,100.]),
    camera_matrix=np.array([[0.,0.,-12.],[8.,0.,0.,],[0.,6.,0.,]]),
    screen_width=800, screen_height=600)

_perspective1 = Perspective(
    scene=_scene, camera_position=np.array([0.,20.,50.]), camera_matrix=np.array([[0.,0.,-12.],[8.,0.,0.,],[0.,4.,0.,]]),
    screen_width=800, screen_height=400)
_perspective2 = Perspective(
    scene=_scene, camera_position=np.array([0.,-20.,10.]), camera_matrix=np.array([[0.,0.,-12.],[8.,0.,0.,],[0.,4.,0.,]]),
    screen_width=800, screen_height=400)

menu = Scene2D()
menu.add_item(uid=0, item=Button(), layer=0)
menu.add_item(uid=1, item=Button(text="Quit"), layer=0)
menu.move_item(0, (100,100))
menu.move_item(1, (100,200))
menu_view = TopDown(menu, screen_width=None, screen_height=None)


for floor in FLOORS:
    _scene.add_item(floor)
for wall in WALLS:
    _scene.add_item(wall)
_scene.add_player(StandingItem(5., 10., np.array([0., 0., 0.,])))
_world = World([_scene])

clock = pygame.time.Clock()
screen = pygame.display.set_mode((1800,1000))
worlds = [_world]
displayer = Displayer(screen)
game = Game(displayer, worlds)

############
game.add_view(menu_view, 7, (700, 200), (300, 600))
############
game.add_view(_perspective1, 3, (950, 50), (800, 400))
game.add_view(_perspective1, 4, (50, 550), (800, 400))
game.add_view(_perspective2, 5, (950, 550), (800, 400))
game.add_view(_perspective2, 6, (50, 50), (800, 400))
############
#game.add_view(_perspective0, 3, (50, 50), (1600, 600))
############

# event_manager = EventManager()
# sound_mixer = SoundMixer()
# enhanced_input = EnhancedUserInput()

def main():
    while True:
        # rethink main loop...
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return 0
                KEYBOARD1.get(event.key, (lambda game: None))(game)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                try:    
                    game.move_player(event.pos, FPS)
                except TypeError as e:
                    print(e)
        # for event in pygame.event.get():
        #     event_manager.broadcast(event)
        # enhanced_input.tick() # always one frame behind ??
        game.tick()
        for world in worlds:
            world.tick()
        displayer.tick()
        # sound_mixer.tick()
        clock.tick(FPS) # what if there's free time to do other (than display) stuff??

main()
