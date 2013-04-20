import pygame, os

import afr.screen

def load_icon(path):
    '''Load an icon using path relative to res/'''
    image = pygame.image.load(os.path.join('res', path))
    image = image.convert()
    return pygame.transform.smoothscale(image, (afr.screen.TILE_WIDTH, afr.screen.TILE_HEIGHT))
