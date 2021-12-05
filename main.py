# main file!
import pygame

from bin import game
from bin.engine import *

import random


def main():
    # create all necessary objects
    window_scale_size = (1920, 1080)
    window_blit_location = (0, 0)

    Window = window.Window(1280, 720, "WageWar.io", pygame.HWACCEL | pygame.HWSURFACE | pygame.RESIZABLE)
    Clock = clock.Clock()
    Handler = handler.Handler()
    World = handler.World()
    InputHandler = handler.InputHandler()
    Camera = camera.Camera(pos=(0, 0), area=window_scale_size)

    # init engine
    game.init()

    frame_buffer = pygame.Surface(window_scale_size, pygame.SRCALPHA, 32).convert()

    # create a warrior!
    for i in range(10):
        Handler.add_entity(game.warrior.Warrior((random.randint(0, 1920), random.randint(0, 1080)),
                                                frame=random.randint(0, 4)))

    running = True
    Clock.start()
    while running:

        # render stuff and update everything
        frame_buffer.fill((255, 255, 255))
        Handler.update(Clock.delta_time)
        Camera.update(Clock.delta_time)
        Camera.render(Handler, frame_buffer)

        # render the frame_buffer onto the screen
        Window.get_window().blit(pygame.transform.scale(frame_buffer, Window.area), window_blit_location)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.WINDOWRESIZED:
                Window.change_dimension(e.x, e.y)
            elif e.type == pygame.KEYUP or e.type == pygame.KEYDOWN:
                InputHandler.update(e)

        pygame.display.flip()
        Clock.update()
        Clock.wait()


if __name__ == "__main__":
    main()
