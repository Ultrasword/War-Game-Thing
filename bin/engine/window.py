import pygame


class Window:
    def __init__(self, width, height, title=None, flags=0, bit_depth=32, icon=None):
        pygame.init()
        self.base_area = (width, height)
        self.area = (width, height)
        self.title = title
        self.icon = icon

        # create the window
        self.window = pygame.display.set_mode(self.area, flags, bit_depth)
        self.size_changed = True

        if self.title:
            pygame.display.set_caption(self.title)
        if self.icon:
            pygame.display.set_icon(pygame.image.load(self.icon))

    def get_window(self):
        return self.window

    def change_dimension(self, width, height):
        self.area = (width, height)
        self.size_changed = True
