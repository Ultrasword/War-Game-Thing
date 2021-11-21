import pygame
import os


def load_animation_from_spritesheet(path, width, height, frames, xoffset, yoffset):
    # open the image file and cut out the areas for frames
    print(path)
    sprite_sheet = FileHandler.get_image(path)
    frame_data = []
    sheet_width = sprite_sheet.get_width()
    sheet_height = sprite_sheet.get_height()
    img_dimensions = (width, height)
    xsection = width + 2 * xoffset
    ysection = height + 2 * yoffset

    # loop through until reach the end of the sprite sheet
    count = 0
    for y in range(0, sheet_height//xsection):
        for x in range(0, sheet_width//ysection):
            # check if out of range
            if count >= frames:
                return frame_data

            # load the new image
            rect = pygame.Rect(xoffset + xsection * x,
                               yoffset + ysection * y,
                               width, height)
            
            # rect = pygame.Rect(x * width, y * height, width, height)
            img = pygame.Surface(img_dimensions, flags=pygame.SRCALPHA, depth=32)
            img.blit(sprite_sheet, (0, 0), rect)

            frame_data.append(img)
            count += 1

    return frame_data


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
        img = pygame.image.load(path).convert()
        FileHandler.images[path] = img
        return img
