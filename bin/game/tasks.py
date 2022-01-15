import pygame
from bin.engine import taskqueue, handler, state
from bin import maths

TASK_OBJECT = taskqueue.Task


class Load_Chunk(TASK_OBJECT):
    def __init__(self, x, y, world, camera_pos, simplex=None, biome=None):
        super(Load_Chunk, self).__init__(taskqueue.HEAVY)
        # load the data
        if simplex:
            self.simplex = simplex
        else:
            self.simplex = world.simplex_gen
        if biome:
            self.biome = biome
        else:
            self.biome = world.biome
        self.pos = (x, y)
        self.y = 0
        self.left = handler.CHUNK_BLOCK_WIDTH * x
        self.top = handler.CHUNK_BLOCK_HEIGHT * y
        self.tasks = [self.load_y_layer for _ in range(handler.CHUNK_BLOCK_HEIGHT+1)]
        self.chunk = world.get_chunk(f"{self.pos[0]}.{self.pos[1]}", auto_start=False)
        self.chunk.terrain = pygame.Surface((handler.CHUNK_BLOCK_WIDTH, handler.CHUNK_BLOCK_HEIGHT),
                                            0, 32).convert_alpha()
        self.cam_pos = camera_pos

    def load_y_layer(self, world, dt):
        # load y layer
        col = (127, 127, 127)
        for x in range(handler.CHUNK_BLOCK_WIDTH):
            value = self.biome.filter2d(self.simplex,
                                        (x + self.left) / handler.CHUNK_BLOCK_WIDTH,
                                        (self.y + self.top) / handler.CHUNK_BLOCK_HEIGHT)
            c = self.biome.color_func(value)
            self.chunk.terrain.set_at((x, self.y), c)
        self.y += 1

    def post_completion(self, world, dt):
        # scale the finished chunk image
        self.chunk.terrain = pygame.transform.scale(self.chunk.terrain, (handler.CHUNK_SIZE_PIX,
                                                                         handler.CHUNK_SIZE_PIX))

    def __lt__(self, other):
        if other.cam_pos:
            dis1 = maths.fast_square((self.cam_pos[0] - self.pos[0])**2 + (self.cam_pos[1] - self.pos[1])**2)
            dis2 = maths.fast_square((other.cam_pos[0] - other.pos[0])**2 + (other.cam_pos[1] - other.pos[1])**2)
            return dis1 < dis2
        else:
            return True


class InitiateChunks(TASK_OBJECT):
    QUEUE_COUNT = 2
    UPDATE_COUNT = 2

    def __init__(self, chunks):
        super(InitiateChunks, self).__init__(taskqueue.LIGHT)
        self.chunks = chunks
        self.current_chunk = 0
        self.tasks = self.queue_chunk

    def get_next_task(self):
        return self.tasks

    def queue_chunk(self, world, dt):
        for i in range(InitiateChunks.UPDATE_COUNT):
            if self.current_chunk >= len(self.chunks):
                self.finished = True
                break
            # queue chunk into task queue
            taskqueue.queue_heavy_task(Load_Chunk(self.chunks[self.current_chunk][0],
                                                      self.chunks[self.current_chunk][1],
                                                      world, state.CAMERA.chunkpos))
            self.current_chunk += 1

