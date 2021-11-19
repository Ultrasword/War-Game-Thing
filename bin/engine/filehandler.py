import pygame
import os


class FileHandler:
    images = {}

    @staticmethod
    def get_image(path):
        if not path:
            return
        # check if file exists
        if not os.path.exists(path):
            return
        # get the image file
        if FileHandler.images.get(path):
            return FileHandler.images.get(path)
        # if not already loaded, load it in
        FileHandler.images[path] = pygame.image.load(path).convert()
        return FileHandler.images[path]

