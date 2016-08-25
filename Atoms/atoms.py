import pygame
import numpy as np
from copy import deepcopy
from random import randint

FPS = 60
pygame.init()

class Particle(object):
    def __init__(self, velocity=np.array([100., 80.]), pos=np.array([0., 0.]), radius=10, color=(0, 0, 0)):
        self.color = color
        self.velocity = velocity
        self.pos = pos
        self.radius = radius

        
class Atom(Particle):
    def __init__(self, energy=6, velocity=np.array([100., 80.]), pos=np.array([0., 0.]), radius=10, color=(255, 0, 0)):
        super(Atom, self).__init__(velocity, pos, radius, color)
        # which energy level
        self.E = None
        self.set_energy(energy)
        self.target_E = 4
        self.number_of_energy_levels = 5
        self.cooldown = 0

    def set_energy(self, new_energy):
        self.E = new_energy
        self.color = (self.E*20, self.E*20, self.E*20)
        
class Photon(Particle):
    def __init__(self, energy=(4,6), velocity=np.array([100., 80.]), pos=np.array([0., 0.]), radius=10, color=(0, 255, 0)):
        super(Photon, self).__init__(velocity, pos, radius)
        # from which level to which
        self.E = energy
        self.color = (0,255,0)
        
class Game(object):
    def __init__(self):
        self.atoms = []
        self.photons = []
        self.surface = pygame.display.set_mode((800,600))
        self.myfont = pygame.font.SysFont("monospace", 15)

    def tick(self):
        for particle in self.atoms + self.photons:
            particle.pos += particle.velocity/float(FPS)
            particle.pos = np.mod(particle.pos, np.array((800, 600)))

        for atom in self.atoms:
            if atom.cooldown > 0:
                atom.cooldown -= 1 
            
        for atom in self.atoms:
            for photon in self.photons:
                if np.linalg.norm(atom.pos - photon.pos) < (atom.radius + photon.radius):
                    if atom.E == min(photon.E) and atom.cooldown == 0:
                        print 'wymuszenie1'
                        atom.set_energy(max(photon.E))
                        self.photons.remove(photon)
                        atom.cooldown = 150 #fix this someday
                    elif atom.E == max(photon.E) and atom.cooldown == 0:
                        print 'wymuszenie2'
                        self.photons.append(deepcopy(photon))
                        atom.set_energy(min(photon.E))
                        atom.cooldown = 150 #fix this someday

                        
        pygame.draw.rect(self.surface, (0, 0, 0), (0,0,800,600))
        for particle in self.atoms + self.photons:
            try:
                pygame.draw.circle(self.surface, particle.color, particle.pos.astype(np.int64), particle.radius)
            except TypeError:
                print particle.color
                raise

        label = self.myfont.render("Number of Photons: " + str(len(self.photons)), 1, (255,255,255))
        self.surface.blit(label, (543, 543))

            
clock = pygame.time.Clock()
game = Game()
#game.atoms.append(Atom(pos=np.array((800.,600.)), velocity=np.array((-350.,0.))))
#game.photons.append(Photon(velocity=np.array((240.,0))))

for _ in xrange(40):
    energy = randint(0, 7)
    pos = np.array([randint(0,799), randint(0,599)]).astype(np.float64)
    velocity = np.array([randint(-120,120), randint(-120,120)]).astype(np.float64)
    game.atoms.append(Atom(energy=energy, velocity=velocity, pos=pos))

for _ in xrange(30):
    energy = (randint(0, 7), randint(0, 7))
    if energy[0] == energy[1]:
        energy = (4,3)
    pos = np.array([randint(0,799), randint(0,599)]).astype(np.float64)
    velocity = np.array([randint(-180,180), randint(-180,180)]).astype(np.float64)
    velocity = np.random.normal(size=(2,))
    if np.linalg.norm(velocity) == 0.:
        velocity = np.array([1,0])
    else:
        velocity /= np.linalg.norm(velocity)
    velocity *= 180.
    game.photons.append(Photon(energy=(4,6), velocity=velocity, pos=pos))

while True:
    game.tick()
    clock.tick(FPS)
    pygame.display.flip()
