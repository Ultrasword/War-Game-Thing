from bin.maths import mod, fast_square as fs
from bin.engine import filehandler
from bin.engine import handler


class Entity:
    def __init__(self, pos=None, area=None, image_file=None, search_radius=0):
        self.pos = list(pos)
        self.area = list(area)
        self.center = [pos[0] + area[0]//2, pos[1] + area[1]//2]
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
        self.chunk = [mod(self.pos[0], handler.CHUNK_SIZE_PIX),
                      mod(self.pos[1], handler.CHUNK_SIZE_PIX)]
        self.motion = [0, 0]
        self.offsets = [0, 0]
        self.hitbox_offsets = [0, 0]
        self.lerp_amt = [0, 0]
        self.speed_multipliers = [0, 0]
        self.xflip = False

    def update_pos(self):
        if not self.dirty:
            return
        self.center = [self.pos[0] + self.area[0] // 2, self.pos[1] + self.area[1] // 2]
        self.dirty = False

    def update(self, h, dt):
        pass

    def distance_to(self, other):
        other.update_pos()
        self.update_pos()
        op = other.pos
        return fs((op.pos[0] - self.pos[0]) ** 2 + (op.pos[1] - self.pos[1]) ** 2)


# some functions for world handling
# TODO - add more functions and some ideas on what the game entities can do
def find_nearby(entity, world_state):
    # find all nearby entities in nearby chunks
    # find search radius
    search_radius = entity.search_radius                            # the radius
    search_width = round(search_radius / handler.BLOCK_SIZE)        # the search width - chunk
    start_chunk = entity.chunk                                      # the current chunk
    search_half_width = search_width // 2                           # the half search width - chunk

    # visible entities
    result = []

    # find chunks
    for i in range(-search_half_width, search_half_width+1):
        for j in range(-search_half_width, search_half_width+1):
            p = f"{i}.{j}"
            c = world_state.world.get_chunk(p)
            # get each entity id - for each entity in the chunk
            for e in c.entities:
                ent = world_state.handler.entities[e]
                # calculate distance
                dis = entity.distance_to(ent)
                if dis > search_radius:
                    result.append(ent)

    # return result
    return sorted(result)


