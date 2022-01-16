import json
from . import handler, particle
from collections import deque


STATE_STACK = deque([])
CURRENT_STATE = None
CAMERA = None
USER = None


def init(camera):
    global CAMERA
    CAMERA = camera


def push_state(state):
    global CURRENT_STATE
    STATE_STACK.append(state)
    CURRENT_STATE = state


def remove_state():
    STATE_STACK.popleft()


def push_left(state):
    STATE_STACK.appendleft(state)
    if len(STATE_STACK) <= 1:
        global CURRENT_STATE
        CURRENT_STATE = state


class GameState:

    def __init__(self, entities=None, chunks=None, seed=None):
        if not entities:
            entities = []
        if not chunks:
            chunks = []
        self.handler, self.world, self.particle = handler.Handler(), handler.World(seed=seed), particle.ParticleHandler()
        self.handler.add_entities(entities)
        self.world.add_chunks(chunks)
        self.systems = {}

    def update_cam(self, dt, camera):
        pass

    def update(self, dt):
        self.handler.update(dt)
        self.particle.update_particles(dt)
        # self.world.update()

    def render(self, window):
        self.world.render(window)
        self.handler.render(window)
        self.particle.render_particles(window)

    def update_systems(self, dt):
        for system in self.systems.values():
            system.update(self.world, self.handler, dt)

    def render_systems(self, window):
        for system in self.systems.values():
            system.render(window)

    def add_entity(self, entity):
        self.handler.add_entity(entity)
        self.world.add_entity(entity.id, entity.chunk_str)

    def add_chunk(self, chunk):
        self.world.add_chunk(chunk)

    def add_entities(self, entities):
        self.handler.add_entities(entities)

    def add_chunks(self, chunks):
        self.world.add_chunks(chunks)

    def add_particle(self, x, y, mx, my, life, img_path, size=None, frame_time=None, custom_func=None):
        self.particle.add_particle(x, y, mx, my, life, img_path, size=size, frame_time=frame_time, custom_func=custom_func)

    def add_system(self, name, system):
        self.systems[name] = system

    def remove_system(self, name):
        self.systems.pop(name)


def load_scene(path, scene=None):
    result = None
    if not scene:
        result = GameState()
    with open(path, 'r') as file:
        decoded = json.load(file)
        file.close()
    # entities should be named as the following
    # {x, y, width, height, imagedata}
    # load entities
    for entity in decoded['entities']:
        x, y, w, h, imgdata = entity
        # TODO - WORK IN PROGRESS | add the other stuff
