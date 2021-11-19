# main file!
import pygame

from bin import engine
from bin.engine import clock
from bin.engine import window
from bin.engine import engine


def main():
    # create all necessary objects
    Window = window.Window(1280, 720, "WageWar.io", pygame.HWACCEL | pygame.HWSURFACE | pygame.RESIZABLE)
    Clock = clock.Clock()

    frame_buffer = pygame.Surface((1920, 1080), pygame.SRCALPHA, 32).convert()
    window_scale_size = (1920, 1080)
    window_blit_location = (0, 0)

    running = True
    Clock.start()
    while running:

        # render stuff and update everything
        frame_buffer.fill((255, 255, 255))

        # render the frame_buffer onto the screen
        Window.get_window().blit(pygame.transform.scale(frame_buffer, window_scale_size), window_blit_location)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        pygame.display.update()
        Clock.start()
        Clock.wait()


if __name__ == "__main__":
    main()
