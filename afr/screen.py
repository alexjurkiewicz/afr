import pygame

RES_X = 1024
RES_Y = 768
TILE_WIDTH = TILE_HEIGHT = 32

# Display init
pygame.init()
screen = pygame.display.set_mode((RES_X, RES_Y))
CAMERA_TILES_X = RES_X // TILE_WIDTH
CAMERA_TILES_Y = RES_Y // TILE_HEIGHT
