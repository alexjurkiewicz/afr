import pygame, logging

import afr.entity

RES_X = 1024
RES_Y = 768
TILE_WIDTH = TILE_HEIGHT = 32

# Display init
pygame.init()
screen = pygame.display.set_mode((RES_X, RES_Y))
CAMERA_TILES_X = RES_X // TILE_WIDTH
CAMERA_TILES_Y = RES_Y // TILE_HEIGHT

global screen

def init_screen():
    global screen
    screen = pygame.display.set_mode((RES_X, RES_Y))
    screen.fill((0,0,0))

def draw_map(m, screen, startx=0, starty=0, clamp_to_map=True):
    '''Draw the map starting from x,y'''
    screen.fill((0,0,0))

    # Clamp draw rectangle to map border
    if clamp_to_map:
        if startx + CAMERA_TILES_X > m.width:
            startx = m.width - CAMERA_TILES_X
        if starty + CAMERA_TILES_Y > m.height:
            starty = m.height - CAMERA_TILES_Y

        startx = 0 if startx < 0 else startx
        starty = 0 if starty < 0 else starty

    # Don't try to draw tiles beyond the edge of the map
    endx = max([min([startx + CAMERA_TILES_X, m.width]), 0])
    endy = max([min([starty + CAMERA_TILES_Y, m.height]), 0])
    
    logging.debug("Drawing map from %s, %s to %s, %s" % (startx, starty, endx, endy))

    for j in range(starty, endy):
        for i in range(startx, endx):
            if i >= 0 and j >= 0:
                screen.blit(m.getTile(i, j).tile.icon, (TILE_WIDTH*(i-startx), TILE_HEIGHT*(j-starty)))

    entities_to_draw = {}
    for e in afr.entity.entities:
        if e.has_component('corporeal'):
            if startx <= e.x <= endx and starty <= e.y <= endy:
                z = e.zorder
                if z in entities_to_draw:
                    entities_to_draw[z].append(e)
                else:
                    entities_to_draw[z] = [e]
    for z in sorted(entities_to_draw.keys()):
        for e in entities_to_draw[z]:
            screen.blit(e.icon, ((e.x-startx)*TILE_WIDTH, (e.y-starty)*TILE_HEIGHT))