from bin import maths


class Camera:
    def __init__(self, offsets=None, pos=None, area=None, entity=None, lerp_amt=3):
        # base variables
        self.offsets = offsets
        self.pos = pos
        self.area = area
        self.entity = entity
        self.lerp_amt = lerp_amt

        if not self.offsets:
            self.offsets = [0, 0]
        if not self.pos:
            self.pos = [0, 0]
        if not self.area:
            self.area = [1920, 1080]

        # other variables
        self.center = [self.area[0] // 2, self.area[1] // 2]

    def update(self, dt):
        # move the camera towards the entity
        if not self.entity:
            return
        # if there is an entity, move towards it
        self.pos = [maths.lerp(self.pos[0], self.entity.pos[0], self.lerp_amt * dt),
                    maths.lerp(self.pos[1], self.entity.pos[1], self.lerp_amt * dt)]

    def update_render_entities(self, handler, frame, dt):
        for entity in handler.entities:
            entity.update(handler, dt)
            frame.blit(entity.image, (entity.pos[0] + entity.offsets[0] + self.offsets[0],
                                      entity.pos[1] + entity.offsets[1] + self.offsets[1]))
