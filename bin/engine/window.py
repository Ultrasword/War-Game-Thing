import pygame


class Window:
    def __init__(self, width, height, title=None, flags=0, bit_depth=32, icon=None):
        self.base_area = (width, height)
        self.area = (width, height)
        self.title = title
        self.icon = icon

        # create the window
        self.window = pygame.display.set_mode(self.area, flags, bit_depth)

    def get_window(self):
        return self.window
