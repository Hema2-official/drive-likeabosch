import pygame
import math
from common_types import *
import random

screen_size = (800, 800)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("drive #likeabosch")

warnings_offset = 0

def clear_screen():
    screen.fill((255, 255, 255))

def float_to_screen(p):
    # ivert
    p = (-p[0], -p[1])
    # convert a 2d point from -80.0 to 80.0 to screen coordinates
    y = int((p[0] + 60.0) / 120.0 * screen_size[1])
    x = int((p[1] + 60.0) / 120.0 * screen_size[0])
    return (x, y)

def abs_dist_to_screen_dist(dist): # meters to pixels
    # convert a distance from -80.0 to 80.0 to screen coordinates
    return int(dist / 120.0 * screen_size[0])

def dist_between_points(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)

# def float_to_screen_dist(dist):
#     p1 = (dist, 0)
#     p1 = float_to_screen(p1)
#     return p1[1]

# def dist_between_points(p0, p1):
#     return ((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)**0.5

def nearest_point_on_rect_rel(p, rect_w, rect_h, rect_center):
    # get the nearest point of the rectangle's corners to the point
    # and return the relative position of that point
    # get the points of the rectangle
    p0 = (rect_center[0] - rect_w / 2, rect_center[1] - rect_h / 2)
    p1 = (rect_center[0] + rect_w / 2, rect_center[1] - rect_h / 2)
    p2 = (rect_center[0] + rect_w / 2, rect_center[1] + rect_h / 2)
    p3 = (rect_center[0] - rect_w / 2, rect_center[1] + rect_h / 2)
    # get the distances to the points
    d0 = dist_between_points(p, p0)
    d1 = dist_between_points(p, p1)
    d2 = dist_between_points(p, p2)
    d3 = dist_between_points(p, p3)
    # get the nearest point
    min_d = min(d0, d1, d2, d3)
    if min_d == d0:
        return (p0[0] - rect_center[0], p0[1] - rect_center[1])
    elif min_d == d1:
        return (p1[0] - rect_center[0], p1[1] - rect_center[1])
    elif min_d == d2:
        return (p2[0] - rect_center[0], p2[1] - rect_center[1])
    elif min_d == d3:
        return (p3[0] - rect_center[0], p3[1] - rect_center[1])

imgs_path = "assets/images/"
img_yoke = pygame.transform.scale(pygame.image.load(imgs_path + "yoke.png").convert_alpha(), (160, 100))
imgs = {
    1: pygame.transform.rotate(pygame.transform.scale(pygame.image.load(imgs_path + "truck.png").convert_alpha(), (48, 15)), 90.0),
    2: pygame.transform.rotate(pygame.transform.scale(pygame.image.load(imgs_path + "car.png").convert_alpha(), (16, 34)), 180.0),
    3: pygame.transform.scale(pygame.image.load(imgs_path + "motorbike.png").convert_alpha(), (16, 8)),
    4: pygame.transform.scale(pygame.image.load(imgs_path + "bicycle.png").convert_alpha(), (16, 8)),
    6: pygame.transform.rotate(pygame.transform.scale(pygame.image.load(imgs_path + "car.png").convert_alpha(), (40, 13)), 180.0)
}

def draw_rect(p0, p1, p2, p3, color):
    # convert 2d points to screen coordinates
    p0 = float_to_screen(p0)
    p1 = float_to_screen(p1)
    p2 = float_to_screen(p2)
    p3 = float_to_screen(p3)
    # draw the rectangle
    pygame.draw.polygon(screen, color, (p0, p1, p2, p3))

def draw_circle(p, color, radius):
    # convert 2d points to screen coordinates
    p = float_to_screen(p)
    radius = abs_dist_to_screen_dist(radius)
    # draw the circle
    pygame.draw.circle(screen, color, p, radius)

def draw_line(p0, p1, color=(255,255,255), thickness=1):
    # convert 2d points to screen coordinates
    p0 = float_to_screen(p0)
    p1 = float_to_screen(p1)
    # draw the line
    pygame.draw.line(screen, color, p0, p1, thickness)


def draw_image(img, p, center=(0, 0), angle=0, abs_pos=False):
    # convert 2d points to screen coordinates
    if not abs_pos:
        p = float_to_screen(p)
    # center = float_to_screen(center)
    # draw the image
    if angle != 0:
        img = pygame.transform.rotate(img, angle)
    screen.blit(img, (p[0] - center[0], p[1] - center[1]))

def draw_text(text, p, color=(255,255,255)):
    # draw the text
    font = pygame.font.SysFont("Roboto", 20)
    text = font.render(text, True, color)
    screen.blit(text, p)

def draw_object(obj, ref):
    # if type is ObjType.noDetection skip
    if obj.obj_type == 0:
        return
    # if the position is 0,0 skip
    if obj.dx == 0 and obj.dy == 0:
        return
    # if obj.prob < 0.5 skip
    if obj.prob != None and obj.prob < 0.5:
        return
    # if type is ObjType.undefined draw a blue circle
    if obj.obj_type == -1 or obj.obj_type == ObjType.undefined:
        draw_circle((obj.dx, obj.dy), (0, 0, 255), 1.0)
        return
    # if type is ObjType.pedestrian draw a red circle
    if obj.obj_type == 5:
        draw_circle((obj.dx, obj.dy), (255, 0, 0), 1.0)
        return
    # draw the objects as images
    center = nearest_point_on_rect_rel((0, 0), imgs[obj.obj_type].get_size()[0], imgs[obj.obj_type].get_size()[1], float_to_screen((obj.dx, obj.dy))) # !!!!!! replace truck with obj.obj_type AND replace (0,0) with rendering position !!!!!!
    draw_image(imgs[obj.obj_type], (obj.dx, obj.dy), (8, 17)) # !!!!!! replace truck with obj.obj_type !!!!!!

def draw_warning(warning, position):
    font = pygame.font.SysFont("Roboto", 35)
    text = font.render(warn_text[warning], True, (255, 0, 100)).convert_alpha()
    # replace alpha layer with white
    text.fill((255, 255, 255, 255), None, pygame.BLEND_RGBA_MULT)
    # draw the text
    screen.blit(text, position)

def draw_warnings(delta_time):
    # get the keys from warn_timeouts with values > 0
    warnings = [k for k, v in warn_timeouts.items() if v > 0]
    # if there are no warnings, return
    if len(warnings) == 0:
        return
    # draw the warnings
    for i, warning in enumerate(warnings):
        draw_warning(warning, (20, i * 40 + 480))
    # decrease the timeouts
    for warning in warnings:
        warn_timeouts[warning] -= delta_time

class Background():
    # downwards scrolling background from a jpg image with a variable speed
    def __init__(self, img_path):
        # load image and resize to screen size
        self.img = pygame.transform.scale(pygame.image.load(img_path).convert(), screen_size)
        self.speed = 0
        self.y_rel = 0
        self.y = 0

    def update(self, speed, delta_time):
        self.speed = speed
        self.y_rel += self.speed * delta_time
        self.y = abs_dist_to_screen_dist(self.y_rel)
        if self.y > screen_size[1]:
            self.y_rel = 0
            self.y = 0
    
    def draw(self):
        screen.blit(self.img, (0, self.y))
        screen.blit(self.img, (0, self.y - screen_size[1]))

class LaneLines():
    # scrolling lane lines which turn with the car (based on the yaw rate)
    def __init__(self, color=(255,255,255)):
        self.color = color
        self.yaw_rate = 0

    def update(self, yaw_rate):
        self.yaw_rate = yaw_rate

    def draw(self):
        # draw two lane lines curved by the yaw rate
        pass