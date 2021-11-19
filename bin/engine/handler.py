from collections import deque

ENTITY_COUNT_LIMIT = int(1e5)


class Handler:
    def __init__(self):
        # entity list
        self.entities = deque(0 for i in range(ENTITY_COUNT_LIMIT+1))

        # active entity -> very dynamic
        # will constantly add and remove entities to update
        self.active_entities = deque([])


class World:
    def __init__(self):

        # should just be a 2D world so chunks are not required
        # there is also a limited amount of world space available
        # TODO - perlin noise
        self.chunks = deque([])
