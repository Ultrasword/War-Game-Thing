# main file!
import os
import json
import pygame
import random

from pygame._sdl2.video import Window as sdlWindow

from bin import game
from bin.engine import *
from bin.engine import state, particle, event, taskqueue


os.environ['SDL_VIDEO_CENTERED'] = '1'
ChunkObject = handler.Chunk


def main():
    # create all necessary objects
    window_scale_size = (1920, 1080)
    window_blit_location = (0, 0)
    RENDER_DISTANCE = 2
    BACKGROUND_COLOR = (255,255,255)

    Window = window.Window(1280, 720, "WageWar.io", pygame.BLEND_RGBA_MAX | pygame.RESIZABLE, bit_depth=32)
    Window.sdlwindow = sdlWindow.from_display_module()
    Window.set_min_size(1280, 720)
    Clock = clock.Clock(60)
    # Handler = handler.Handler()
    # World = handler.World()
    InputHandler = handler.InputHandler()

    # init engine
    game.init()
    state.init(inputhandler=InputHandler, camera=camera.Camera(window_size=window_scale_size))
    frame_buffer = pygame.Surface(window_scale_size, pygame.SRCALPHA, 32).convert()

    state.push_state(game.gamestates.InGame(camera_pos=[window_scale_size[0]//2, window_scale_size[1]//2], seed=1))
    # state.CURRENT_STATE.add_particle(100, 100, 30, 30, 20, "assets/animations/warrior/warrior_attack.png")
    # faster loading chunks instead of re-creating every time
    # testing purposes only
    for x in range(3):
        for y in range(3):
            state.CURRENT_STATE.add_chunk(ChunkObject(x, y,
                terrain=pygame.image.load(f"assets/test/fastload/{x}.{y}.png").convert()))

    state.CURRENT_STATE.world.calculate_relavent_chunks(state.CAMERA.chunkpos, RENDER_DISTANCE, l_bor=0, t_bor=0, r_bor=100,
                                                        b_bor=100)
    # print(state.CURRENT_STATE.world.active_chunks)
    taskqueue.set_pause_loops(2)

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
                state.CURRENT_STATE.world.calculate_relavent_chunks(state.CAMERA.chunkpos, RENDER_DISTANCE, l_bor=0, t_bor=0)
            else:
                # do later
                pass

        # get camera moving
        state.CURRENT_STATE.update_cam(Clock.delta_time, state.CAMERA)

        # render stuff and update everything
        frame_buffer.fill(BACKGROUND_COLOR)

        # update tasks
        taskqueue.update_heavy_task(state.CURRENT_STATE.world, Clock.delta_time)
        taskqueue.update_light_task(state.CURRENT_STATE.world, Clock.delta_time)

        # render with camera
        state.CAMERA.render_and_update_with_camera(state.CURRENT_STATE, frame_buffer, Clock.delta_time)

        # render the frame_buffer onto the screen
        Window.window.blit(pygame.transform.scale(frame_buffer, Window.area), window_blit_location)

        pygame.display.flip()
        Clock.update()
        Clock.wait()


if __name__ == "__main__":
    main()
