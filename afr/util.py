import pygame, os

import afr.screen

def load_icon(path):
    '''Load an icon using path relative to res/'''
    image = pygame.image.load(os.path.join('res', path))
    image = image.convert()
    return pygame.transform.smoothscale(image, (afr.screen.TILE_WIDTH, afr.screen.TILE_HEIGHT))

def clamp(i, minimum, maximum):
    if minimum > maximum:
        raise ValueError("Minimum must be equal to or less than maximum")
    return max(min(maximum, i), minimum)