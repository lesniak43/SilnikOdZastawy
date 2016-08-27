import numpy as np
import pygame

from classes import *
from data import WALLS, FLOORS, KEYBOARD1, FPS

pygame.init()


_perspective0 = PerspectiveStereo(
    camera_position=np.array([0.,20.,100.]), camera_matrix=np.array([[0.,0.,-12.],[8.,0.,0.,],[0.,6.,0.,]]),
    screen_x=0, screen_y=0, screen_width=800, screen_height=600)
_perspective1 = Perspective(
    camera_position=np.array([0.,20.,50.]), camera_matrix=np.array([[0.,0.,-12.],[8.,0.,0.,],[0.,6.,0.,]]),
    screen_x=0, screen_y=0, screen_width=800, screen_height=600)
_perspective2 = Perspective(
    camera_position=np.array([0.,-20.,10.]), camera_matrix=np.array([[0.,0.,-12.],[8.,0.,0.,],[0.,6.,0.,]]),
    screen_x=0, screen_y=0, screen_width=800, screen_height=600)
_scene = Scene3D(id_=0, views=[_perspective0, _perspective2])
#_scene = Scene3D(id_=0, views=[_perspective1, _perspective2])
for floor in FLOORS:
    _scene.add_item(floor)
for wall in WALLS:
    _scene.add_item(wall)
_scene.add_player(StandingItem(5., 10., np.array([0., 0., 0.,])))
_world = World([_scene])

clock = pygame.time.Clock()
#surface = pygame.display.set_mode((800,600))
surface = pygame.display.set_mode((1600,600))
worlds = [_world]
displayer = Displayer(surface, worlds)
game = Game(displayer, worlds)
# event_manager = EventManager()
# sound_mixer = SoundMixer()
# enhanced_input = EnhancedUserInput()

while True:
    # rethink main loop...
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            KEYBOARD1.get(event.key, (lambda game: None))(game)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            try:    
                game.move_player(event.pos, FPS)
            except TypeError as e:
                print e
    # for event in pygame.event.get():
    #     event_manager.broadcast(event)
    # enhanced_input.tick() # always one frame behind ??
    game.tick()
    for world in worlds:
        world.tick()
    displayer.tick()
    # sound_mixer.tick()
    clock.tick(FPS) # what if there's free time to do other (than display) stuff??
