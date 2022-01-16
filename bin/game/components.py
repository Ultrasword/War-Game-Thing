import pygame
from bin.engine import state, ui
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


class UserDragVisualiser(Component):
    def __init__(self):
        super(UserDragVisualiser, self).__init__()
        self.start_selection = False
        self.start_point = (0, 0)
        self.end_point = (0, 0)

    def update(self, world, handler, dt):
        # if not started selection, turn on start selection
        if state.USER.mouse.pressed[ui.MOUSEBUTTON_LEFT]:
            if not self.start_selection:
                self.start_selection = True
                self.start_point = state.USER.mouse.get_pos()
                self.end_point = self.start_point
            # else, set end point
            else:
                self.end_point = state.USER.mouse.get_pos()
        # if not pressing - stop the selection and clear it
        else:
            self.start_selection = False
            self.start_point = (0, 0)
            self.end_point = (0, 0)
        # print(self.start_point, self.end_point)

    def render(self, window):
        # draw the rectangle
        if self.start_selection:
            offsets = state.CAMERA.half_area
            pygame.draw.lines(window, (255, 0, 0), True,
                             (self.start_point,
                              (self.start_point[0], self.end_point[1]),
                              self.end_point,
                              (self.end_point[0], self.start_point[1])), 1)

