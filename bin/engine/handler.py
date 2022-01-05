import json
import pygame
from collections import deque
from bin.engine import filehandler

ENTITY_COUNT_LIMIT = int(1e5)
CHUNK_SIZE = 16
BLOCK_SIZE = 128
CHUNK_SIZE_PIX = CHUNK_SIZE * BLOCK_SIZE


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

    def render(self, window):
        window.blits([[e.image, [e.pos[0] + e.offsets[0], e.pos[1] + e.offsets[1]]]
                      for e in self.entities.values() if e.image])

    def give_id(self):
        self.ENTITY_ID_COUNT += 1
        return self.ENTITY_ID_COUNT

    def add_entity(self, entity):
        entity.id = self.give_id()
        self.entities[entity.id] = entity
        # add to active
        self.active_entities.append(entity.id)

    def add_entities(self, entities):
        map(self.add_entity, entities)

    def remove_entity(self, eid):
        self.entities[eid] = None
        # check if its in active_entities
        # during next update


class Chunk:
    def __init__(self, x, y, data=None):
        # block = [img_pointer, x, y, w, h, z]
        self.blocks = deque(data if data else [])
        self.pos = f"{x}.{y}"
        # a list of ids
        self.entities = set()

    def render(self, window):
        window.blits([[filehandler.LOADED_IMAGES[b[0]], (b[0], b[1])] for b in self.blocks if b])


class World:
    def __init__(self):

        # should just be a 2D world so chunks are not required
        # there is also a limited amount of world space available
        # TODO - perlin noise and find out how big the world is -> ask ethan
        self.chunks = {}
        self.active_chunks = []

    def get_chunk(self, pos):
        result = self.chunks.get(pos)
        if result:
            return result
        x, y = map(int, pos.split("."))
        self.chunks[pos] = Chunk(x, y)

    def add_chunk(self, chunk):
        self.chunks[chunk.pos] = chunk

    def add_chunks(self, chunks):
        map(self.add_chunk, chunks)

    def render(self, window):
        for chunk in self.active_chunks:
            chunk.render(window)


def change_mapped_key(key_num, value):
    InputHandler.default_key_map[key_num] = value


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
