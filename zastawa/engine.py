#############################################################
####      WEAKREF THEM LIKE THERE'S NO TOMORROW !!!      ####
#############################################################

import math
from weakref import ref, proxy

import pygame
import numpy as np


def _three_points_to_plane(points):
    cr = np.cross(points[1] - points[0], points[2] - points[0])
    plane = np.array([cr[0], cr[1], cr[2], - np.inner(cr, points[0])])
    return plane

def _make_axis_rotation_matrix(direction, angle):
    """
    https://mail.scipy.org/pipermail/numpy-discussion/2009-March/040806.html
    Create a rotation matrix corresponding to the rotation around a general
    axis by a specified angle.
    R = dd^T + cos(a) (I - dd^T) + sin(a) skew(d)
    Parameters:
        angle : float a
        direction : array d
    """
    d = np.array(direction, dtype=np.float64)
    d /= np.linalg.norm(d)
    eye = np.eye(3, dtype=np.float64)
    ddt = np.outer(d, d)
    skew = np.array([[    0,  d[2],  -d[1]],
                     [-d[2],     0,  d[0]],
                     [d[1], -d[0],    0]], dtype=np.float64)
    mtx = ddt + np.cos(angle) * (eye - ddt) + np.sin(angle) * skew
    return mtx


class DiskStorage(object):
    pass
    # save/load everything? cache here??


class Animation(object):
    def __init__(self, images):
        pass
    def get_image(self):
        pass

class Item(object):
    # scenery - static or dynamic, position? sound? images?
    # orientation
    def __init__(self, animations, position, orientation=np.eye(3), color=(0,255,0)):
        self.color = color
        self.position_ = position
        self.orientation_ = orientation
        self.state_ = "standing"
        self.path_ = []
        self.speed_ = 0.
    def get_image(self):
        return self.animations[0][0]
    def animation_tick(self):
        pass
    def orient_towards(self, new_position):
        pass
#        self.how_to_draw_me_parameters
#        self.how_to_sound_parameters
#    def drawme()
#    def soundme()
#    def _load_images()
#    def _load_sounds()
#    def _free_memory?()

class Floor(Item):
    def __init__(self, animations, corner_a, corner_b, color):
        assert corner_a[1] == corner_b[1]
        self.corners = [
            corner_a,
            np.array([corner_a[0], corner_a[1], corner_b[2]]),
            corner_b,
            np.array([corner_b[0], corner_a[1], corner_a[2]]),
        ]
        super(Floor, self).__init__(animations, position=np.array([0,0,0]), color=color)

class StandingItem(Item):

    def __init__(self, width, height, position):
        self.width = width
        self.height = height
        self.position_ = position
        super(StandingItem, self).__init__([], position, color=(255,0,0))

class StraightWall(Item):
    def __init__(self, animations, corner_a, corner_b):
        self.corners = [
            corner_a,
            np.array([corner_a[0], corner_b[1], corner_a[2]]),
            corner_b,
            np.array([corner_b[0], corner_a[1], corner_b[2]]),
        ]
        super(StraightWall, self).__init__(animations, position=np.mean(self.corners))


class Scene(object):
    def __init__(self, id_):
        self.items_ = []
        self.id_ = id_

    def add_item(self, item):
        self.items_.append(item)

    def add_player(self, item):
        self.player_ = item
        self.add_item(item)

    def set_active_view(self, index):
        try:
            self.active_view_ = self.views_[index]
        except (IndexError, TypeError):
            pass

class Button(Item):

    def __init__(self, color=(100, 150, 100), text="Zastawa", width=200, height=50):
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.myfont = pygame.font.SysFont("monospace", 15)
        label = self.myfont.render(text, 1, (255,255,255))
        self.image.blit(label, (10, 10))

class Scene2D(Scene):
# menu, chessboard etc.
    def __init__(self, ):
        self._layer_items = {}
        self._items = {}

    def add_item(self, uid, item, layer):
        assert isinstance(layer, int)
        assert layer >= 0
        assert uid not in self._items
        self._items[uid] = item
        if not layer in self._layer_items:
            self._layer_items[layer] = []
        self._layer_items[layer].append(uid)
        
    def get_layers(self):
        return sorted(self._layer_items.keys())

    def get_items(self, layer=None):
        result = []
        if layer is None:
            for layer in self.get_layers():
                for item_uid in self._layer_items[layer]:
                    result.append((item_uid, proxy(self._items[item_uid])))
        else:
            for item_uid in self._layer_items[layer]:
                result.append((item_uid, proxy(self._items[item_uid])))
        return result

    def move_item(self, uid, coords, layer=None):
        assert layer is None # todo implement
        self._items[uid].rect.x = coords[0]
        self._items[uid].rect.y = coords[1]

class Scene3D(Scene):

    def __init__(self, id_):
        super(Scene3D, self).__init__(id_)

    def find_path(self, start_point, end_point, speed, fps=60):
        # veeeeeery unoptimized
        dist = np.linalg.norm(start_point - end_point)
        path_len = dist * fps / speed
        return list(reversed(np.vstack((np.linspace(start_point[i], end_point[i], path_len + 1) for i in xrange(3))).T))[:-1]

    def tick(self):
        for item in self.items_:
            item.animation_tick()
            if len(item.path_) > 0:
                item.state_ = "moving"
                new_pos = item.path_.pop()
                if not self.check_collision(item, new_pos):
                    item.orient_towards(new_pos)
                    item.position_ = new_pos
                else:
                    item.path_ = []
                    item.state_ = "collision"
            else:
                item.state_ = "standing"

    def check_collision(self, item, new_position):
        return False


class HexItem(Item):

    def __init__(self, uid, hex_position=np.array((0,0,0)), speed=1, color=(0,0,0)):
        self.uid = uid
        self.hex_position = hex_position
        self.true_hex_position = (hex_position, hex_position)
        self.path = []
        self.hex_path = []
        self.speed = speed
        self.color = color
        self.timeout = 0

class SceneHex(Scene):

    def __init__(self, id_):
        super(SceneHex, self).__init__(id_)
        self.e1 = np.array((0, 1, -1))
        self.e2 = np.array((-1, 1, 0))
        self.e3 = np.array((-1, 0, 1))
        self.items = []
        

        # example code
        # self._mode = 0
        self._mode = 1
        self.TIMEOUT = 43
        self.MAX_PER_HEX = 2

        self._occupied = {}

    def occupy_true_hex_position(self, item, true_hex_position):
        self._occupied[item.uid] = tuple(true_hex_position[1])

    def can_move(self, item, true_hex_position):
        if item.uid not in self._occupied:
            return True
        elif self._occupied[item.uid] == tuple(true_hex_position[1]):
            return True
        elif self._occupied.values().count(tuple(true_hex_position[1])) < self.MAX_PER_HEX:
            return True
        else:
            return False

    def find_path(self, start_hex, end_hex, speed=1, fps=60):
        delta = end_hex - start_hex
        path = [start_hex]
        hex_path = [(start_hex, start_hex)]
        for step in [self.e1, self.e2, self.e3, -self.e1, -self.e2, -self.e3]:
            while np.sum(np.abs(end_hex - (path[-1] + step))) < np.sum(np.abs(end_hex - path[-1])):
                hex_path += (fps / speed) * [(path[-1].astype(np.int64), (path[-1] + step).astype(np.int64))]
                if self._mode == 0:
                    path += (fps / speed) * [path[-1] + step]
                elif self._mode == 1:
                    path += list(np.vstack([np.linspace(np.array(path[-1])[i], (path[-1] + step)[i], (fps / speed)) for i in xrange(3)]).T)
                else:
                    raise ValueError()
        return list(reversed(path)), list(reversed(hex_path))

    def tick(self):
        for item in self.items:
            if len(item.path) > 0:
                if self.can_move(item, item.hex_path[-1]):
                    item.hex_position = item.path.pop()
                    item.true_hex_position = item.hex_path.pop()
                    self.occupy_true_hex_position(item, item.true_hex_position)
                    item.timeout = 0
                else:
                    item.timeout += 1
                if item.timeout >= self.TIMEOUT:
                    item.path = []
                    item.hex_path = []
            else:
                pos = np.random.randint(-10, 10) * self.e1 + np.random.randint(-10, 10) * self.e2 + np.random.randint(-10, 10) * self.e3
                #x = np.random.randint(-10, 10)
                #y = np.random.randint(-10, 10)
                #z = - (x + y)
                #pos = np.array((x, y, z))
                item.path, item.hex_path = self.find_path(item.hex_position, pos, speed=item.speed)

    def get_items(self):
        return self.items

class SceneView(object):
    def __init__(self, scene):
        self.scene = proxy(scene) if scene is not None else None
        pass
    def screenshot(self, filename):
        pass

class SceneView2D(SceneView):
    def __init__(self, scene):
        super(SceneView2D, self).__init__(scene)

class SceneView3D(SceneView):
    def __init__(self, scene):
        super(SceneView3D, self).__init__(scene)


class HexView(SceneView3D):
    def __init__(self, scene):
        super(HexView, self).__init__(scene)
        self.projection = np.array([[-np.sqrt(3)/6., np.sqrt(3)/3., -np.sqrt(3)/6.], [1./2., 0., -1./2.]])
        self.immersion = 2 * self.projection.T # ???
        self.e1 = np.array((0, 1, -1))
        self.e2 = np.array((-1, 1, 0))
        self.e3 = np.array((-1, 0, 1))
        self.scale = 15
        self.offset = np.array((400, 300))

    def project(self, coords):
        return (np.dot(self.projection, coords) * self.scale + self.offset).astype(np.int64)

    def draw_scene(self, surface):
        surface.fill((255, 255, 255))
        for item in self.scene.get_items():
            pygame.draw.circle(surface, item.color, self.project(item.hex_position), 5)

    def describe(self, coords):
        return np.dot(self.immersion, np.array(coords).reshape(-1,1))

    def describe_hex(self, coords, L=0):
        x, y, z = coords
        point = np.array((int(math.floor(x)), int(math.floor(y)), L - int(math.floor(x)) - int(math.floor(y))))
        candidates = [point, point + self.e1, point - self.e1, point + self.e2, point - self.e2, point + self.e3, point - self.e3]
        return candidates[np.argmin([np.linalg.norm(c - np.array(coords)) for c in candidates])] 



"""
class Isometric(SceneView3D):
    def __init__(self, scene, projection, immersion):
        super(Isometric, self).__init__(scene)
        self.projection = projection
        self.immersion = immersion

    def draw_scene(self, surface):
        for _, item in self.scene.get_items():
            surface.blit(item.image, item.rect)

    def describe(self, coords):
        return np.dot(self.immersion, np.array(coords).reshape(-1,1))
"""

class World(object):
    def __init__(self, scenes):
        self.scenes_ = scenes
        self.active_scene_ = self.scenes_[0]
    def tick(self):
        self.active_scene_.tick()




class TopDown(SceneView2D):

    def __init__(self, scene, screen_width=None, screen_height=None):
        super(TopDown, self).__init__(scene)
        self.screen_width = screen_width
        self.screen_height = screen_height

    def draw_scene(self, surface):
        for _, item in self.scene.get_items():
            surface.blit(item.image, item.rect)

    def describe(self, coords):
        for uid, item in reversed(self.scene.get_items()):
            if item.rect.collidepoint(coords):
                return uid
        return None

            

class Camera3D(object):
    # so unoptimized...
    #
    # camera_matrix - orthogonal matrix:
    # e1 - from camera position to center of field of view
    # e2 - from f.o.w. center to right center
    # e3 - from f.o.w. center to top center
    def __init__(self, position, camera_matrix):
        self.position_ = position
        self.matrix = camera_matrix
        self._update()

    def _update(self):
        self.e1_ = self.matrix[0]
        self.e2_ = self.matrix[1]
        self.e3_ = self.matrix[2]
        self.E1_ = np.inner(self.e1_, self.e1_)
        self.E2_ = np.inner(self.e2_, self.e2_)
        self.E3_ = np.inner(self.e3_, self.e3_)

    def rotate_x(self, theta):
        self.matrix = np.dot(self.matrix, _make_axis_rotation_matrix(self.e2_, theta))
        self._update()

    def rotate_y(self, theta):
        self.matrix = np.dot(self.matrix, _make_axis_rotation_matrix(self.e3_, theta))
        self._update()

    def rotate_z(self, theta):
        self.matrix = np.dot(self.matrix, _make_axis_rotation_matrix(self.e1_, theta))
        self._update()

    def move_forward(self, dist):
        self.position_ += dist * self.e1_ / np.sqrt(self.E1_)

    def move_right(self, dist):
        self.position_ += dist * self.e2_ / np.sqrt(self.E2_)

    def move_up(self, dist):
        self.position_ += dist * self.e3_ / np.sqrt(self.E3_)

class Camera3DStereo(object):
    # incorrect, but works for now
    def __init__(self, camera1, camera2):
        self.c1 = camera1
        self.c2 = camera2

    def rotate_x(self, theta):
        self.c1.rotate_x(theta)
        self.c2.rotate_x(theta)

    def rotate_y(self, theta):
        self.c1.rotate_y(theta)
        self.c2.rotate_y(theta)

    def rotate_z(self, theta):
        self.c1.rotate_z(theta)
        self.c2.rotate_z(theta)

    def move_forward(self, dist):
        self.c1.move_forward(dist)
        self.c2.move_forward(dist)

    def move_right(self, dist):
        self.c1.move_right(dist)
        self.c2.move_right(dist)

    def move_up(self, dist):
        self.c1.move_up(dist)
        self.c2.move_up(dist)

class PerspectiveStereo(SceneView3D):

    def __init__(self, scene, camera_position, camera_matrix,
                 screen_width, screen_height):
        super(PerspectiveStereo, self).__init__(scene)
        self.screen_width = screen_width
        self.screen_height = screen_height

        self._delta_camera = np.array([3.,0.,0.])
        self.p1 = Perspective(scene, camera_position, camera_matrix,
                              screen_width, screen_height)
        self.p2 = Perspective(scene, camera_position - self._delta_camera, camera_matrix,
                              screen_width, screen_height)
        self.camera = Camera3DStereo(self.p1.camera, self.p2.camera)

    def draw_scene(self, surface):
        s1 = surface.subsurface(pygame.Rect(0, 0, self.screen_width, self.screen_height))
        s2 = surface.subsurface(pygame.Rect(self.screen_width, 0, self.screen_width, self.screen_height))
        self.p1.draw_scene(s1)
        self.p2.draw_scene(s2)

    def describe(self, xy, plane):
        if xy[0] >= self.screen_width:
            return self.p2.describe((xy[0]-self.screen_width, xy[1]), plane)
        else:
            return self.p1.describe(xy, plane)

class Perspective(SceneView3D):

    def __init__(self, scene, camera_position, camera_matrix,
                 screen_width, screen_height):
        super(Perspective, self).__init__(scene)
        self.camera = Camera3D(camera_position, camera_matrix)
        self.screen_width = screen_width
        self.screen_height = screen_height

        self._f_draw = {
            StraightWall: self._draw_straight_wall,
            Floor: self._draw_floor,
            StandingItem: self._draw_standing_item,
        }

    def to_surface_coords(self, point):
        a = point - self.camera.position_
        A1 = np.inner(a, self.camera.e1_)
        A2 = np.inner(a, self.camera.e2_)
        A3 = np.inner(a, self.camera.e3_)
        if A1 < self.camera.E1_:
            return None, None
        x = int(self.screen_width * (1. + (A2*self.camera.E1_)/(A1*self.camera.E2_)) / 2.)
        y = int(self.screen_height * (1. - (A3*self.camera.E1_)/(A1*self.camera.E3_)) / 2.)
        if x < 0 or x >= self.screen_width or y < 0 or y > self.screen_height:
            return x, y
#            return None, None
        else:
            return x, y

    def draw_scene(self, surface):
        scene = self.scene
        # totally wrong order
        self.draw_background(surface)
        _items = []
        for item in scene.items_:
            if isinstance(item, Floor):
                self.draw_item(item, surface)
            else:
                _items.append((np.linalg.norm(self.camera.position_ - item.position_), item))
        for _, item in reversed(sorted(_items)):
            self.draw_item(item, surface)

    def draw_background(self, surface):
        surface.fill((200, 200, 255))

    def draw_item(self, item, surface):
        if type(item) in self._f_draw.keys():
            self._f_draw[type(item)](surface, item)

    def _draw_straight_wall(self, surface, sw):
        # sw.get_image
        try:
            pygame.draw.polygon(surface, sw.color, [self.to_surface_coords(corner) for corner in sw.corners])
        except TypeError: # some points are None
            pass

    def _draw_floor(self, surface, sw):
        # sw.get_image
        try:
            pygame.draw.polygon(surface, sw.color, [self.to_surface_coords(corner) for corner in sw.corners])
        except TypeError: # some points are None
            pass

    def _draw_standing_item(self, surface, item):
        scale = self.camera.E1_ / np.inner(self.camera.e1_, item.position_ - self.camera.position_)
        if scale > 0. and scale < 10.:
            draw_pos = self.to_surface_coords(item.position_)
            if draw_pos[0] is not None:
                draw_w = int(item.width * scale * self.screen_width / (2 * np.sqrt(self.camera.E2_)))
                draw_h = int(item.height * scale * self.screen_height / (2 * np.sqrt(self.camera.E3_)))
                pygame.draw.rect(surface, item.color, (draw_pos[0] - draw_w/2, draw_pos[1] - draw_h, draw_w, draw_h))
                # surface.blit(pygame.transform.scale(image, (item.width * scale, item_height * scale)), pos - half_w + h)

    def describe(self, xy, plane):
        A, B, C, D = plane
        e = self.camera.e1_ + (2. * float(xy[0]) / float(self.screen_width) - 1.) * self.camera.e2_ + (1. - 2. * float(xy[1]) / float(self.screen_height)) * self.camera.e3_
        denominator = np.inner(e, np.array([A, B, C]))
        if denominator != 0.:
            l = - (np.inner(self.camera.position_, np.array([A, B, C])) + D) / denominator
            if l > 0.:
                return self.camera.position_ + l * e
            else:
                return None
        else:
            return None


class Displayer(object):

    def __init__(self, screen):
        self.screen = screen
        # let's start with ten layers and see if we ever need more...
        self.views = [None, None, None, None, None, None, None, None, None, None]
        self.rects = [None, None, None, None, None, None, None, None, None, None]
        self.surfaces = [None, None, None, None, None, None, None, None, None, None]

    def add_view(self, view, layer, dest=(0, 0), shape=(800, 600)):
        self.views[layer] = view
        self.rects[layer] = pygame.Rect(dest, shape)
        self.surfaces[layer] = pygame.Surface(shape)

    def _to_layer_coords(self, layer, coords):
        return (coords[0] - self.views[layer][1][0], coords[1] - self.views[layer][1][1])

    def describe(self, coords):
        for i in reversed(xrange(len(self.views))):
            rect = self.rects[i]
            if rect is not None and rect.collidepoint(coords):
                x, y = coords
                return self.views[i], (x - rect.x, y - rect.y)
        return None, None

    def register_scene_object_to_description(self,):
        pass

    def tick(self):
#        self.screen.fill((0,0,0))
        for i in xrange(len(self.views)):
            if self.views[i] is not None:
                view = self.views[i]
                surface = self.surfaces[i]
                rect = self.rects[i]
                view.draw_scene(surface)
#                surface = surface.convert_alpha()
#                surface.fill((255, 255, 255, 100), None, pygame.BLEND_RGBA_MULT)
                self.screen.blit(surface, rect)
        pygame.display.update() # add rectangle_list !
#        pygame.display.update(pygame.Rect(300,300,200,200))




class Controller(object):
    def __init__(self, ):
        pass


class EnhancedUserInput(object):
    def __init__(self, list_of_controllers, rules):
        pass
    def tick(self):
        pass









class EventManager(object):

    def __init__(self, ):
        pass

    def broadcast(self, event):
        # how? to whom?
        pass
    #    if event.type == pygame.QUIT:
    #        done = True
    #    if event.type == pygame.MOUSEBUTTONDOWN:
    #        print event.button
    #    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
