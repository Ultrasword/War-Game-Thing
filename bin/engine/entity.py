from bin.engine import filehandler


class Entity:
    def __init__(self, pos=None, area=None, image_file=None):
        self.pos = pos
        self.area = area
        self.image_file = image_file

        if not self.pos:
            self.pos = [0, 0]
        if not self.area:
            self.area = [0, 0]
        if not self.image_file:
            self.image = filehandler.FileHandler.get_image(image_file)

        self.hitbox = [self.pos[0], self.pos[1], self.area[0], self.area[1]]
        self.offsets = [0, 0]
        self.hitbox_offsets = [0, 0]
        self.lerp_amt = [0, 0]

    def update(self, handler, dt):
        pass


