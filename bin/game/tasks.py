import pygame
import pickle
import numpy as np
from bin.engine import taskqueue, handler, state
from bin.engine.multiprocesshandling import PROCESS_SHARED_ARRAY_SPACE
from bin import maths


TASK_OBJECT = taskqueue.Task


class EndProcess(TASK_OBJECT):
    def __init__(self, shared_memory, data):
        """For end game - its just so that the function runs"""
        super(EndProcess, self).__init__(shared_memory)

    def run(self, send, uid):
        pass


class LoadChunk(TASK_OBJECT):
    def __init__(self, shared_memory, data):
        """For loading chunks"""
        super(LoadChunk, self).__init__(shared_memory)
        # data = [biome, simplex, chunk_pos]
        self.biome = data[0]
        self.simplex = data[1]
        self.pos = data[2]
        # i want chunks to load layer by layer
        self.width = handler.CHUNK_BLOCK_WIDTH
        self.height = handler.CHUNK_BLOCK_HEIGHT
        self.chunk_str = ".".join([str(x) for x in self.pos])
        self.terrain = np.ndarray((self.width, self.height, 3))

    def run(self, send, uid):
        l = self.width * self.pos[0]
        t = self.height * self.pos[1]
        for y in range(self.height):
            for x in range(self.width):
                value = self.biome.filter2d(self.simplex, (x + l) / self.width, (y + t) / self.height)
                self.terrain[x][y] = self.biome.color_func(value)

                # set result in to the results array
                # get an available index
        send.send((self.result, self.chunk_str, self.terrain))

    def result(self, world, args):
        world.get_chunk(args[0]).terrain = pygame.transform.scale(pygame.surfarray.make_surface(args[1]),
                                        (handler.CHUNK_SIZE_PIX, handler.CHUNK_SIZE_PIX)).convert()





