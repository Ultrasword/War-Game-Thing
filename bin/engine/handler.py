import json
import pygame
from PIL import Image as PIL_Image
from collections import deque
from bin import maths
from bin.engine import event
from bin.engine import filehandler
from bin.engine import taskqueue
from bin.engine import state
from bin.game import worldgeneration
from bin.game import tasks

ENTITY_COUNT_LIMIT = int(1e5)
CHUNK_SIZE = 16
BLOCK_SIZE = 64
CHUNK_SIZE_PIX = CHUNK_SIZE * BLOCK_SIZE
CHUNK_BLOCK_WIDTH = 20
CHUNK_BLOCK_HEIGHT = 20
WORLD_CHUNK_WIDTH = 30
WORLD_CHUNK_HEIGHT = 30

# simplex noise
SIMPLEX_NOISE = None


class Handler:
    ENTITY_ID_COUNT = 0

    def __init__(self):
        # entity list
        self.entities = {}

        # active entity -> very dynamic
        # will constantly add and remove entities to update
        # holds only entity ids -> the position of the entity in the self.entities list
        self.active_entities = deque([])

    def update(self, world, dt):
        for eid, entity in self.entities.items():
            if not entity:
                self.entities.pop(eid)
                continue
            entity.update(self, world, dt)
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


def get_chunk(x, y, biome, simplex):
    """Loads Chunks given the x and y position of a chunk"""
    l = CHUNK_BLOCK_WIDTH * x
    t = CHUNK_BLOCK_HEIGHT * y
    # TODO - set a designated color deciding function
    col = (127, 127, 127)
    biome_data = pygame.Surface((CHUNK_BLOCK_WIDTH, CHUNK_BLOCK_HEIGHT), pygame.SRCALPHA, 32).convert()
    for y in range(CHUNK_BLOCK_WIDTH):
        for x in range(CHUNK_BLOCK_HEIGHT):
            value = biome.filter2d(simplex, (x+l) / CHUNK_BLOCK_WIDTH, (y+t) / CHUNK_BLOCK_HEIGHT)
            biome_data.set_at((x,y), biome.color_func(value))
    return biome_data


def save_terrain(directory, chunkx, chunky, terrain):
    pil_image = PIL_Image.frombytes("RGBA", terrain.get_size(), pygame.image.tostring(terrain, "RGBA", False))
    pil_image.save(f"{directory}/{chunkx}.{chunky}.png")


class Chunk:

    def __init__(self, x, y, data=None, terrain=None):
        # block = [img_pointer, x, y, w, h, z]
        self.blocks = deque(data if data else [])
        # also terrain deque
        self.raw_terrain = terrain
        self.terrain = None
        # the pos string
        self.pos = f"{x}.{y}"
        # the chunk position offset
        self.x = x
        self.y = y
        self.pos_offset = (x * CHUNK_SIZE_PIX, y * CHUNK_SIZE_PIX)
        # a list of ids
        self.entities = set()

    def start(self, simplex, biome):
        if not self.raw_terrain:
            self.raw_terrain = get_chunk(self.x, self.y, biome, simplex)
            # save_terrain("assets/test/fastload", self.x, self.y, self.terrain)
        self.terrain = pygame.transform.scale(self.raw_terrain, (CHUNK_SIZE_PIX, CHUNK_SIZE_PIX))

    def render(self, window, world, offset=(0,0)):
        # 2 stage rendering process
        # render the terrain -> terrain should be one singular pygame surface object
        # window.blit(pygame.transform.scale(self.terrain, (CHUNK_SIZE_PIX, CHUNK_SIZE_PIX)),
        #            (self.pos_offset[0] + offset[0], self.pos_offset[1] + offset[1]))
        window.blit(self.terrain, (self.pos_offset[0] + offset[0], self.pos_offset[1] + offset[1]))
        window.blits([[filehandler.get_image(b[0], (b[3], b[4])), (b[1] + offset[0], b[2] + offset[1])] for b in self.blocks])

    def add_block(self, block):
        self.blocks.append(block)

    def add_entity(self, eid):
        self.entities.add(eid)

    def entity_in_chunk(self, eid):
        return eid in self.entities

    def remove_entity(self, eid):
        self.entities.remove(eid)


class World:
    def __init__(self, seed=None, biome=None):
        # should just be a 2D world so chunks are not required
        # there is also a limited amount of world space available
        # TODO - perlin noise and find out how big the world is -> ask ethan
        self.chunks = {}
        self.active_chunks = []
        self.simplex_gen = worldgeneration.WorldGenerator(seed=seed)
        self.biome = biome if biome else worldgeneration.Biome()
        self.chunk_loader = tasks.InitiateChunks([])
        self.textures = {}

    def calculate_relavent_chunks(self, focus_point, render_distance, l_bor=0, r_bor=WORLD_CHUNK_WIDTH, t_bor=0,
                                  b_bor=WORLD_CHUNK_HEIGHT):
        """Recalculates all relavent chunks in order to lower cpu usage - should be used on chunk change event"""
        center_chunk = (maths.mod(focus_point[0], CHUNK_SIZE_PIX),
                        maths.mod(focus_point[1], CHUNK_SIZE_PIX))
        # clear active chunks
        self.active_chunks.clear()
        queue = []
        # all chunks should be within render distance
        for x in range(-render_distance + center_chunk[0], render_distance + center_chunk[0] + 1):
            if l_bor != None:
                if x < l_bor:
                    continue
            if r_bor != None:
                if x >= r_bor:
                    continue
            for y in range(-render_distance + center_chunk[1], render_distance + center_chunk[1] + 1):
                if t_bor != None:
                    if y < t_bor:
                        continue
                if b_bor != None:
                    if y >= b_bor:
                        continue
                # check if chunk exists
                p_string = f"{x}.{y}"
                self.active_chunks.append(p_string)
                if not self.get_chunk(p_string):
                    queue.append((x, y))
        taskqueue.queue_light_task(tasks.InitiateChunks(queue))
        # print(self.active_chunks)

    def get_chunk(self, posstring, create=True, auto_start=True):
        result = self.chunks.get(posstring)
        if result:
            return result
        if not create:
            return
        x, y = map(int, posstring.split("."))
        result = Chunk(x, y)
        self.chunks[posstring] = result
        if auto_start:
            result.start(self.simplex_gen, self.biome)
        return result

    def add_chunk(self, chunk):
        chunk.start(self.simplex_gen, self.biome)
        self.chunks[chunk.pos] = chunk

    def add_chunks(self, chunks):
        map(self.add_chunk, chunks)

    def add_entity(self, eid, chunk_str):
        self.get_chunk(chunk_str).add_entity(eid)

    def render(self, window):
        for chunk in self.active_chunks:
            self.chunks[chunk].render(window, self)

    def is_collided(self, hitbox, other):
        # block = [img_pointer, x, y, w, h, z]
        if hitbox[0] + hitbox[2] < other[1]:
            return True
        if hitbox[0] > other[1] + other[3]:
            return True
        if hitbox[1] + hitbox[3] < other[2]:
            return True
        if hitbox[1] > other[2] + other[4]:
            return True
        return True

    def get_collided_chunks(self, entity, hitbox):
        if not entity.change_chunks:
            return entity.collided_chunks
        # un toggle it
        entity.change_chunks = False
        # chunk pos string
        cp = entity.chunk_str
        # get chunk
        chunk = self.get_chunk(cp, create=False)
        # create result array
        chunks = []
        # store hitbox leaking
        leaving = [0,0]
        if hitbox[0] < chunk.pos_offset[0]:
            leaving[0] -= 1
        elif hitbox[0] + hitbox[2] > chunk.pos_offset[0] + CHUNK_SIZE_PIX:
            leaving[0] += 1
        if hitbox[1] < chunk.pos_offset[1]:
            leaving[1] -= 1
        elif hitbox[1] + hitbox[3] > chunk.pos_offset[1] + CHUNK_SIZE_PIX:
            leaving[1] += 1

        # now you add all the possible chunks :D, max - 2 x 2 check
        lx = min(0, leaving[0]); rx = max(0, leaving[0])
        ly = min(0, leaving[1]); ry = max(0, leaving[1])
        for x in range(chunk.x + lx, chunk.x + rx+1):
            for y in range(chunk.y + ly, chunk.y + ry+1):
                chunks.append(f"{x}.{y}")
        entity.collided_chunks = chunks
        # [print(chunk, end="\t") for chunk in chunks]; print()
        return chunks

    def move_entity(self, entity):
        # touching = [False, False, False, False]
        #             left   top   right   bottom
        # block = [img_pointer, x, y, w, h, z]

        hit_area = [entity.pos[0] + entity.hitbox_offsets[0],
                    entity.pos[1] + entity.hitbox_offsets[1],
                    entity.area[0], entity.area[1]]
        rounded = (round(entity.motion[0]), round(entity.motion[1]))
        hit_area[0] += entity.motion[0]
        for chunk in self.get_collided_chunks(entity, hit_area):
            # get the blocks in chunk
            # print("chunk: ", chunk)
            for block in self.get_chunk(chunk).blocks:
                if self.is_collided(hit_area, block):
                    # if moving left
                    if rounded[0] < 0:
                        # set position to the right of the block
                        hit_area[0] = block[1] + block[3]
                    elif rounded[0] > 0:
                        # set position to the left of the block
                        hit_area[0] = block[1] - block[3]

        hit_area[1] += entity.motion[1]
        for chunk in self.get_collided_chunks(entity, hit_area):
            # get the blocks in the chunk
            for block in self.get_chunk(chunk).blocks:
                if self.is_collided(hit_area, block):
                    if rounded[1] < 0:
                        # set position to the bottom of the block
                        hit_area[1] = block[2] + block[4]
                    elif rounded[1] > 0:
                        # set position to the left of the block
                        hit_area[1] = block[2] - block[4]

        entity.pos = [hit_area[0] - entity.hitbox_offsets[0], hit_area[1] - entity.hitbox_offsets[1]]
        entity.update_pos(state.CURRENT_STATE.world)


