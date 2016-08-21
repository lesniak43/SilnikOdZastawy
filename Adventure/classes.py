#############################################################
####      WEAKREF THEM LIKE THERE'S NO TOMORROW !!!      ####
#############################################################

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
    def __init__(self, id_, views):
        self.items_ = []
        self.id_ = id_
        self.views_ = views
        self.active_view_ = views[0]
        pass

    def add_item(self, item):
        self.items_.append(item)

    def add_player(self, item):
        self.player_ = item
        self.add_item(item)

class Scene2D(Scene):
# menu, chessboard etc.
    def __init__(self, ):
        pass

class Scene3D(Scene):

    def __init__(self, id_, views):
        super(Scene3D, self).__init__(id_, views)

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

class World(object):
    def __init__(self, scenes):
        self.scenes_ = scenes
        self.active_scene_ = self.scenes_[0]
    def tick(self):
        self.active_scene_.tick()

class SceneView(object):
    def __init__(self, ):
        pass
    def screenshot(self, filename):
        pass

class SceneView2D(object):
    def __init__(self, ):
        pass

class SceneView3D(object):
    def __init__(self, ):
        pass

class Isometric(SceneView3D):
    def __init__(self, ):
        pass




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




class Perspective(SceneView3D):

    def __init__(self, camera_position, camera_matrix,
                 screen_x, screen_y, screen_width, screen_height):
        self.camera = Camera3D(camera_position, camera_matrix)
        self.screen_x = screen_x
        self.screen_y = screen_y
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
        x = int(self.screen_width * (1. + (A2*self.camera.E1_)/(A1*self.camera.E2_)) / 2. + self.screen_x)
        y = int(self.screen_height * (1. - (A3*self.camera.E1_)/(A1*self.camera.E3_)) / 2. + self.screen_y)
        if x < 0 or x >= self.screen_width or y < 0 or y > self.screen_height:
            return x, y
#            return None, None
        else:
            return x, y

    def draw_scene(self, surface, scene):
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
        pygame.display.flip()

    def draw_background(self, surface):
        pygame.draw.rect(surface, (50, 50, 50), (self.screen_x, self.screen_y, self.screen_width, self.screen_height))

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
        e = self.camera.e1_ + (2. * float(xy[0] - self.screen_x) / float(self.screen_width) - 1.) * self.camera.e2_ + (1. - 2. * float(xy[1] - self.screen_y) / float(self.screen_height)) * self.camera.e3_
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

    def __init__(self, surface, worlds):
        self.surface = surface
        self.worlds = worlds
        self.world = self.worlds[0]

    def register_scene(self, scene):
        pass

    def select_scene(self, scene_id):
        pass

    def modify_scene(self, new_params, permament=False):
        pass

    def tick(self, ):
        # something's terribly wrong here
        self.world.active_scene_.active_view_.draw_scene(self.surface, self.world.active_scene_)

    def describe(self, (x, y)):
        pass

    def register_scene_object_to_description(self,):
        pass


class Controller(object):
    def __init__(self, ):
        pass


class EnhancedUserInput(object):
    def __init__(self, list_of_controllers, rules):
        pass
    def tick(self):
        pass

class Game(object):
# send high-level requests to worlds, displayer etc.
    def __init__(self, displayer, worlds):
        self.displayer = displayer
        self.worlds = worlds
        self.active_world = self.worlds[0]
    def tick(self):
        pass
    def camera_move_right(self, dist):
        self.displayer.world.active_scene_.active_view_.camera.move_right(dist)
    def camera_move_up(self, dist):
        self.displayer.world.active_scene_.active_view_.camera.move_up(dist)
    def camera_move_forward(self, dist):
        self.displayer.world.active_scene_.active_view_.camera.move_forward(dist)
    def camera_rotate_x(self, theta):
        self.displayer.world.active_scene_.active_view_.camera.rotate_x(theta)
    def camera_rotate_y(self, theta):
        self.displayer.world.active_scene_.active_view_.camera.rotate_y(theta)
    def camera_rotate_z(self, theta):
        self.displayer.world.active_scene_.active_view_.camera.rotate_z(theta)
    def move_player(self, click_position, fps):
        player = self.active_world.active_scene_.player_
        floor_plane = (0., 1., 0., 0.,)
        player_speed = 12.
        player.path_ = self.active_world.active_scene_.find_path(player.position_, self.active_world.active_scene_.active_view_.describe(click_position, floor_plane), speed=player_speed, fps=fps)









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
