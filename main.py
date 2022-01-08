# main file!
import os
import pygame
import random

from pygame._sdl2.video import Window as sdlWindow

from bin import game
from bin.engine import *
from bin.engine import state, particle, event

os.environ['SDL_VIDEO_CENTERED'] = '1'

ChunkObject = handler.Chunk


def main():
    # create all necessary objects
    window_scale_size = (1920, 1080)
    window_blit_location = (0, 0)
    RENDER_DISTANCE = 2
    BACKGROUND_COLOR = (255,255,255)

    Window = window.Window(1280, 720, "WageWar.io", pygame.HWACCEL | pygame.HWSURFACE | pygame.RESIZABLE)
    Window.sdlwindow = sdlWindow.from_display_module()
    Window.set_min_size(1280, 720)
    Clock = clock.Clock(60)
    # Handler = handler.Handler()
    # World = handler.World()
    InputHandler = handler.InputHandler()
    Camera = camera.Camera(window_size=window_scale_size)
    cam_pos = [window_scale_size[0] // 2, window_scale_size[1] // 2]
    Camera.set_position(cam_pos)

    # init engine
    game.init()
    state.init(inputhandler=InputHandler)
    frame_buffer = pygame.Surface(window_scale_size, pygame.SRCALPHA, 32).convert()

    state.push_state(game.gamestates.InGame(seed=1))
    # state.CURRENT_STATE.add_particle(100, 100, 30, 30, 20, "assets/animations/warrior/warrior_attack.png")
    state.CURRENT_STATE.add_chunk(ChunkObject(0,0))

    state.CURRENT_STATE.world.calculate_relavent_chunks(Camera.chunkpos, RENDER_DISTANCE, l_bor=0, t_bor=0, r_bor=100,
                                                        b_bor=100)
    print(state.CURRENT_STATE.world.active_chunks)

    # create a warrior!
    for i in range(10):
        state.CURRENT_STATE.add_entity(game.warrior.Warrior((random.randint(0, 1920), random.randint(0, 1080)),
                                                frame=random.randint(0, 4)))

    def test():
        # testing space ----------------------------------

        dot = pygame.Surface((5,5), 0, 32)
        dot.fill((255,0,0))

        # ------------------------------------------------
    # test()

    running = True
    Clock.start()
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.WINDOWRESIZED:
                Window.change_dimension(e.x, e.y)
            elif e.type == pygame.KEYUP or e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11 and e.type == pygame.KEYDOWN:
                    Window.toggle_windowed_fullscreen()
                else:
                    InputHandler.update(e)
            elif e.type == event.FOCAL_CHANGE_EVENT_ID:
                state.CURRENT_STATE.world.calculate_relavent_chunks(Camera.chunkpos, RENDER_DISTANCE, l_bor=0, t_bor=0)
            else:
                # do later
                pass

        # get camera moving
        state.CURRENT_STATE.update_cam(Clock.delta_time, Camera)

        # render stuff and update everything
        frame_buffer.fill(BACKGROUND_COLOR)
        # render with camera
        Camera.render_and_update_with_camera(state.CURRENT_STATE, frame_buffer, Clock.delta_time, 2)

        # render the frame_buffer onto the screen
        Window.get_window().blit(pygame.transform.scale(frame_buffer, Window.area), window_blit_location)

        pygame.display.flip()
        Clock.update()
        Clock.wait()


if __name__ == "__main__":
    main()
