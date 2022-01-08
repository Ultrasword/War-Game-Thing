import pygame


def user_event_id():
    pygame.USEREVENT += 1
    return pygame.USEREVENT


# ENUMS
FOCAL_CHANGE_EVENT_ID = user_event_id()

# events
FOCAL_CHANGE_EVENT = pygame.event.Event(FOCAL_CHANGE_EVENT_ID)
