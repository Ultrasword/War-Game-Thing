import pygame
import pickle
import numpy as np

from PIL import Image as PIL_Image

from bin.engine import taskqueue, handler, state
from bin.engine.multiprocesshandling import PROCESS_SHARED_ARRAY_SPACE
from bin import maths


TASK_OBJECT = taskqueue.Task


class EndProcess:
    def __init__(self, shared_memory, data):
        """For end game - its just so that the function runs"""
        pass

    def run(self, send, uid):
        send.send((EndProcess, ()))


class LoadChunk(TASK_OBJECT):
    def __init__(self, shared_memory, data):
        """For loading chunks"""
        super(LoadChunk, self).__init__(shared_memory)
        # data = [biome, simplex, chunk_pos]
        self.biome = data[0]
        self.simplex = data[1]
        self.pos = data[2]
        # print(self.pos)
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
        print("loaded chunk ", self.pos)

    def result(self, world, args):
        chunk = world.get_chunk(args[0], auto_start=False)
        if chunk:
            chunk.raw_terrain = pygame.surfarray.make_surface(args[1])
            chunk.terrain = pygame.transform.scale(chunk.raw_terrain,
                                        (handler.CHUNK_SIZE_PIX, handler.CHUNK_SIZE_PIX)).convert_alpha()


class SaveChunkData(TASK_OBJECT):
    def __init__(self, shared_memory, data):
        """For saving chunks to cache"""
        super(SaveChunkData, self).__init__(shared_memory)
        self.directory = data[0]
        self.x = data[1]
        self.y = data[2]
        self.raw_terrain_image = data[3]
        self.size = data[4]

    def run(self, send, uid):
        pil_image = PIL_Image.frombytes("RGBA", self.size,
                                        self.raw_terrain_image)
        pil_image.save(f"{self.directory}/{self.x}.{self.y}.png")
        send.send((self.result, f"{self.x}.{self.y}", f"{self.directory}/{self.x}.{self.y}.png"))
        print("cached chunk ", self.x, self.y)

    def result(self, world, args):
        # we want to clear the chunk image data
        chunk = world.get_chunk(args[0], create=False)
        if chunk:
            chunk.terrain = None
            chunk.raw_terrain = None
            world.cached_chunks[args[0]] = args[1]


class LoadCacheChunk(TASK_OBJECT):
    def __init__(self, shared_memory, data):
        """For loading cached chunks"""
        super(LoadCacheChunk, self).__init__(shared_memory)
        self.directory = data[0]
        self.x = data[1]
        self.y = data[2]

    def run(self, send, uid):
        # load image using pygame
        img = pygame.image.load(f"{self.directory}/{self.x}.{self.y}.png")
        raw_terrain_image = pygame.image.tostring(img,
                                                  "RGBA", False)
        send.send((self.result, f"{self.x}.{self.y}", raw_terrain_image, img.get_size()))
        print("cache load chunk ", self.x, self.y)

    def result(self, world, args):
        chunk = world.get_chunk(args[0], create=False)
        if chunk:
            chunk.raw_terrain = pygame.image.fromstring(args[1], args[2], "RGBA", False)
            chunk.terrain = pygame.transform.scale(chunk.raw_terrain,
                                            (handler.CHUNK_SIZE_PIX, handler.CHUNK_SIZE_PIX))


