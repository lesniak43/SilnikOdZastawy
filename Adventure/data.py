import pygame

from classes import *

WALLS = [
    StraightWall([], np.array([-50., 30., -200]), np.array([-50., 10., -350])),
    StraightWall([], np.array([-20., 10., -10.]), np.array([10., -5., -20.])),
    StraightWall([], np.array([-100., -50., -50.]), np.array([-90., 50., -20.]))
]

FLOORS = [
    Floor([], np.array([-10., 0., -200.]), np.array([10., 0., -100.]), (255,255,0)),
#    Floor([], np.array([-20., -5., -10.]), np.array([10., -5., -20.]), (0,0,128)),
]

_theta = 0.1
_delta = 10.
KEYBOARD1 = {
    pygame.K_LEFT: lambda game: game.camera_move_right(-_delta),
    pygame.K_RIGHT: lambda game: game.camera_move_right(_delta),
    pygame.K_UP: lambda game: game.camera_move_forward(_delta),
    pygame.K_DOWN: lambda game: game.camera_move_forward(-_delta),
    pygame.K_KP1: lambda game: game.camera_move_up(_delta),
    pygame.K_KP3: lambda game: game.camera_move_up(-_delta),
    pygame.K_KP4: lambda game: game.camera_rotate_y(_theta),
    pygame.K_KP6: lambda game: game.camera_rotate_y(-_theta),
    pygame.K_KP2: lambda game: game.camera_rotate_x(_theta),
    pygame.K_KP8: lambda game: game.camera_rotate_x(-_theta),
    pygame.K_KP7: lambda game: game.camera_rotate_z(_theta),
    pygame.K_KP9: lambda game: game.camera_rotate_z(-_theta),
    pygame.K_1: lambda game: game.set_active_view(0),
    pygame.K_2: lambda game: game.set_active_view(1),
}

FPS = 60

"""
VELOCITY = 500
im_left = [
    pygame.image.load("1/2.png"),
    pygame.image.load("1/1.png"),
    pygame.image.load("1/2.png"),
    pygame.image.load("1/3.png"),
]
im_right = [
    pygame.transform.flip(pygame.image.load("1/2.png"), True, False),
    pygame.transform.flip(pygame.image.load("1/1.png"), True, False),
    pygame.transform.flip(pygame.image.load("1/2.png"), True, False),
    pygame.transform.flip(pygame.image.load("1/3.png"), True, False),
]
im_back = [
    pygame.image.load("1/5.png"),
    pygame.image.load("1/4.png"),
    pygame.image.load("1/5.png"),
    pygame.image.load("1/6.png"),
]
im_front = [
    pygame.image.load("1/8.png"),
    pygame.image.load("1/7.png"),
    pygame.image.load("1/8.png"),
    pygame.image.load("1/9.png"),
]
"""
"""
#http://soundbible.com/tags-hitting.html
snd_hit = pygame.mixer.Sound('hit.ogg')
snd_hit.play()
"""
