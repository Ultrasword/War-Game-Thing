import numpy as np
import pygame

from bin import maths
from bin.engine import state


# constants
CAMERA_MOVE_SPEED = 200
CAMERA_MOTION = [0, 0]
CAMERA_POSITION = [0, 0]
CAMERA_LERP = 0.5


class InGame(state.GameState):
    def __init__(self, entities=None, chunks=None, seed=None):
        super(InGame, self).__init__(entities, chunks, seed)

    def update_cam(self, dt, camera):
        CAMERA_MOTION[0] = maths.lerp(CAMERA_MOTION[0], 0.0, CAMERA_LERP)
        CAMERA_MOTION[1] = maths.lerp(CAMERA_MOTION[1], 0.0, CAMERA_LERP)
        if state.INPUTHANDLER.pressed(pygame.K_LEFT):
            CAMERA_MOTION[0] -= CAMERA_MOVE_SPEED * dt
        if state.INPUTHANDLER.pressed(pygame.K_RIGHT):
            CAMERA_MOTION[0] += CAMERA_MOVE_SPEED * dt
        if state.INPUTHANDLER.pressed(pygame.K_DOWN):
            CAMERA_MOTION[1] += CAMERA_MOVE_SPEED * dt
        if state.INPUTHANDLER.pressed(pygame.K_UP):
            CAMERA_MOTION[1] -= CAMERA_MOVE_SPEED * dt
        CAMERA_POSITION[0] += CAMERA_MOTION[0]
        CAMERA_POSITION[1] += CAMERA_MOTION[1]
        camera.set_position([int(CAMERA_POSITION[0]), int(CAMERA_POSITION[1])])
