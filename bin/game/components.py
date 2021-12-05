import pygame
from bin.engine.component import Component

default_key_map = {
    pygame.K_w: 'up',
    pygame.K_s: 'down',
    pygame.K_d: 'right',
    pygame.K_a: 'left',
    pygame.K_SPACE: 'jump',
    pygame.K_LSHIFT: 'shift',
    pygame.K_ESCAPE: 'esc'
}


class KeyboardController(Component):
    def __init__(self, keymap=None):
        super().__init__()
        if keymap is None:
            keymap = default_key_map
