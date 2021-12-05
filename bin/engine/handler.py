import json
import pygame
from collections import deque

ENTITY_COUNT_LIMIT = int(1e5)


class Handler:
    ENTITY_ID_COUNT = 0

    def __init__(self):
        # entity list
        self.entities = {}

        # active entity -> very dynamic
        # will constantly add and remove entities to update
        # holds only entity ids -> the position of the entity in the self.entities list
        self.active_entities = deque([])

    def update(self, dt):
        for eid, entity in self.entities.items():
            if not entity:
                self.entities.pop(eid)
                continue
            entity.update(self, dt)
            # check if entity in range or not in range
            # everything will be updated regardless of being active or not

    def give_id(self):
        self.ENTITY_ID_COUNT += 1
        return self.ENTITY_ID_COUNT

    def add_entity(self, entity):
        entity.id = self.give_id()
        self.entities[entity.id] = entity
        # add to active
        self.active_entities.append(entity.id)

    def remove_entity(self, eid):
        self.entities[eid] = None
        # check if its in active_entities
        # during next update


class World:
    def __init__(self):

        # should just be a 2D world so chunks are not required
        # there is also a limited amount of world space available
        # TODO - perlin noise and find out how big the world is -> ask ethan
        self.chunks = deque([])


class Scene:
    def __init__(self, datapath=None):
        self.datapath = datapath
        if self.datapath:
            # load the data
            load_scene(self.datapath, self)
        # handler and world
        self.handler = Handler()
        self.world = World()


# TODO - WORK IN PROGRESS
def load_scene(path, scene=None):
    result = None
    if not scene:
        result = Scene()
    with open(path, 'r') as file:
        decoded = json.load(file)
        file.close()
    # entities should be named as the following
    # {x, y, width, height, imagedata}
    # load entities
    for entity in decoded['entities']:
        x, y, w, h, imgdata = entity


class InputHandler:
    default_key_map = {
        pygame.K_w: 'up',
        pygame.K_s: 'down',
        pygame.K_d: 'right',
        pygame.K_a: 'left',
        pygame.K_SPACE: 'jump',
        pygame.K_LSHIFT: 'shift',
        pygame.K_ESCAPE: 'esc'
    }

    def __init__(self):
        self.keymap = InputHandler.default_key_map
        self.key_pressed = {x: False for x in InputHandler.default_key_map.values()}

    def pressed(self, key):
        return self.key_pressed.get(key)

    def update(self, pygame_event):
        if pygame_event.type == pygame.KEYDOWN:
            self.key_pressed[pygame_event.key] = False
        elif pygame_event.type == pygame.KEYUP:
            self.key_pressed[pygame_event.key] = True

