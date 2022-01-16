# main file!
import os
import json
import pygame
import random
from multiprocessing import Process

from pygame._sdl2.video import Window as sdlWindow

from bin import game
from bin.game import components
from bin.engine import *
from bin.engine import state, particle, event, taskqueue, ui


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

    # init engine
    game.init()
    state.init(camera=camera.Camera(window_size=window_scale_size))
    state.USER = ui.User()
    frame_buffer = pygame.Surface(window_scale_size, pygame.SRCALPHA, 32).convert()

    state.push_state(game.gamestates.InGame(camera_pos=[window_scale_size[0]//2, window_scale_size[1]//2], seed=1))
    # state.CURRENT_STATE.add_particle(100, 100, 30, 30, 20, "assets/animations/warrior/warrior_attack.png")
    # faster loading chunks instead of re-creating every time
    # testing purposes only
    for x in range(3):
        for y in range(3):
            state.CURRENT_STATE.add_chunk(ChunkObject(x, y,
                terrain=pygame.image.load(f"assets/test/fastload/{x}.{y}.png").convert()))

    state.CURRENT_STATE.world.calculate_relavent_chunks(state.CAMERA.chunkpos, RENDER_DISTANCE)
    # print(state.CURRENT_STATE.world.active_chunks)
    state.CURRENT_STATE.world.get_chunk("0.0").add_block(["assets/kirb.jpeg", 400, 400, 100, 100, 0])
    taskqueue.set_pause_loops(2)

    # create a warrior!
    # for i in range(10):
    #     state.CURRENT_STATE.add_entity(game.warrior.Warrior((random.randint(0, 1920), random.randint(0, 1080)),
    #                                             frame=random.randint(0, 4)))
    state.CURRENT_STATE.add_entity(game.warrior.Warrior((300, 300), frame=0))
    # add systems
    state.CURRENT_STATE.add_system(0, components.UserDragVisualiser())
    state.USER.mouse.update_ratio(1280, 720, window_scale_size[0], window_scale_size[1])

    running = True
    Clock.start()
    count = 1
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            # window resize
            elif e.type == pygame.WINDOWRESIZED:
                Window.change_dimension(e.x, e.y)
                state.USER.mouse.update_ratio(e.x, e.y, window_scale_size[0], window_scale_size[1])
            # keyboard - keydown
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11:
                    Window.toggle_windowed_fullscreen()
                else:
                    state.USER.keyboard.press_key(e.key)
            # keyboard - keyup
            elif e.type == pygame.KEYUP:
                state.USER.keyboard.release_key(e.key)
            # handle mouse movement
            elif e.type == pygame.MOUSEMOTION:
                state.USER.mouse.mouse_move_update(e)
            # handle mouse press
            elif e.type == pygame.MOUSEBUTTONDOWN:
                state.USER.mouse.mouse_press(e)
                # TODO - remove
                if e.button == 1:
                    p = state.USER.mouse.get_pos()
                    p = (p[0] - state.CAMERA.center[0], p[1] - state.CAMERA.center[1])
                    state.CURRENT_STATE.add_entity(game.warrior.Warrior(p))
                    count += 1
                    print(count)
            elif e.type == pygame.MOUSEBUTTONUP:
                state.USER.mouse.mouse_release(e)
            # special event
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
        state.CURRENT_STATE.update_systems(Clock.delta_time)
        taskqueue.update_heavy_task(state.CURRENT_STATE.world, Clock.delta_time)
        taskqueue.update_light_task(state.CURRENT_STATE.world, Clock.delta_time)

        # render with camera
        state.CAMERA.render_and_update_with_camera(state.CURRENT_STATE, frame_buffer, Clock.delta_time)
        state.CURRENT_STATE.render_systems(frame_buffer)

        # render the frame_buffer onto the screen
        Window.window.blit(pygame.transform.scale(frame_buffer, Window.area), window_blit_location)

        pygame.display.flip()
        Clock.update()
        Clock.wait()


if __name__ == "__main__":
    main()
