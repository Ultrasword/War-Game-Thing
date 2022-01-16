from bin.maths import mod, fast_square as fs
from bin.engine import filehandler
from bin.engine import handler
from bin.engine import state


class Entity:
    def __init__(self, pos=None, area=None, image_file=None, search_radius=0):
        self.pos = list(pos)
        self.area = list(area)
        self.center = [pos[0] + area[0] // 2, pos[1] + area[1] // 2]
        self.image_file = image_file
        self.image = None
        self.id = 0
        self.search_radius = search_radius

        self.dirty = True

        if not self.pos:
            self.pos = [0, 0]
        if not self.area:
            self.area = [0, 0]
        if self.image_file:
            self.image = filehandler.get_image(image_file)

        self.hitbox = [self.pos[0], self.pos[1], self.area[0], self.area[1]]
        self.chunk = [self.pos[0] // handler.CHUNK_SIZE_PIX,
                      self.pos[1] // handler.CHUNK_SIZE_PIX]
        self.chunk_str = f"{self.chunk[0]}.{self.chunk[1]}"
        self.motion = [0, 0]
        self.offsets = [0, 0]
        self.hitbox_offsets = [0, 0]
        self.lerp_amt = [0, 0]
        self.speed_multipliers = [0, 0]
        self.xflip = False

    def update_pos(self, world):
        if self.dirty:
            self.center = [self.pos[0] + self.area[0] // 2, self.pos[1] + self.area[1] // 2]
            self.dirty = False
            # check if chunk changed

            new_chunk = (int(self.center[0] // handler.CHUNK_SIZE_PIX),
                         int(self.center[1] // handler.CHUNK_SIZE_PIX))
            if new_chunk != self.chunk:
                world.get_chunk(self.chunk_str).remove_entity(self.id)
                self.chunk_str = f"{new_chunk[0]}.{new_chunk[1]}"
                world.get_chunk(self.chunk_str).add_entity(self.id)
                self.chunk = new_chunk

    def update(self, h, w, dt):
        pass

    def distance_to(self, other):
        other.update_pos(state.CURRENT_STATE.world)
        self.update_pos(state.CURRENT_STATE.world)
        op = other.pos
        return fs((op.pos[0] - self.pos[0]) ** 2 + (op.pos[1] - self.pos[1]) ** 2)


# some functions for world handling
# TODO - add more functions and some ideas on what the game entities can do
def find_nearby(entity, world):
    # find all nearby entities in nearby chunks
    # find search radius
    search_radius = entity.search_radius  # the radius
    search_width = round(search_radius / handler.BLOCK_SIZE)  # the search width - chunk
    start_chunk = entity.chunk  # the current chunk
    search_half_width = search_width // 2  # the half search width - chunk

    # visible entities
    result = []

    # find chunks
    for i in range(-search_half_width, search_half_width + 1):
        for j in range(-search_half_width, search_half_width + 1):
            p = f"{i}.{j}"
            c = world.world.get_chunk(p)
            # get each entity id - for each entity in the chunk
            for e in c.entities:
                ent = world.handler.entities[e]
                # calculate distance
                dis = entity.distance_to(ent)
                if dis > search_radius:
                    result.append(ent)

    # return result
    return sorted(result)
