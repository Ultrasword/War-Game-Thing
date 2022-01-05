import pygame
import random

from bin.maths import lerp
from bin.engine import entity
from bin.engine import animation


# open the warrior data file
warrior_animations = None
warrior_area = (32, 32)
warrior_lerp_amt = (30, 30)
warrior_hitbox = (8, 8, 4, 4)
warrior_hitbox_offsets = (4, 4)
warrior_offsets = (0, 0)
warrior_search_radius = 100


def init():
    global warrior_animations
    warrior_animations = animation.AnimationData(jsonpath="assets/animations/warrior/warrior.json")


class Warrior(entity.Entity):
    def __init__(self, pos, frame=0):
        super().__init__(pos=pos, area=warrior_area, image_file=None)
        # animation handler!
        self.animation_access = animation.Animation(ani_data=warrior_animations,
                                                    current_animation="idle",
                                                    frame=frame)
        # get image for the warrior
        self.image = self.animation_access.get_frame(warrior_animations)

        # set hitbox and lerp variables
        self.hitbox = warrior_hitbox
        self.offsets = warrior_offsets
        self.hitbox_offsets = warrior_hitbox_offsets
        self.lerp_amt = warrior_lerp_amt

    def update(self, handler, dt):
        # update animation handler
        self.animation_access.update(dt)
        if self.animation_access.frame_changed:
            self.image = self.animation_access.get_frame(warrior_animations, self.xflip)

        # don't move yet!
        # TODO - make movement script and entity AI
        # wander around for now

        self.pos[0] += self.motion[0]
        self.pos[1] += self.motion[1]

        self.motion = [lerp(self.motion[0], 0.0, 0.3), lerp(self.motion[1], 0.0, 0.3)]

        moving = False

        # move the entity in the world!
        # TODO - add world movement and collision detection between objects and entity

        # add lerp!
