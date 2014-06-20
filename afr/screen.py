import pygame, logging

import afr.entity, afr.util

RES_X = 800
RES_Y = 600
TILE_WIDTH = TILE_HEIGHT = 32
CAMERA_TILES_X = RES_X // TILE_WIDTH
CAMERA_TILES_Y = RES_Y // TILE_HEIGHT

global last_x, last_y
last_x, last_y = (0, 0)

def init_screen():
    pygame.init()
    global screen
    screen = pygame.display.set_mode((RES_X, RES_Y))
    screen.fill((0,0,0))
    logging.info("Camera shows %s tiles across and %s down" % (CAMERA_TILES_X, CAMERA_TILES_Y))

def draw_map(m, screen, focus=None, clamp_to_map=True):
    '''Draw the map starting from x,y'''
    screen.fill((0,0,0))
    
    # If we have a focus, ensure it's in the midle of the screen
    if focus:
        half_x = CAMERA_TILES_X // 2
        half_y = CAMERA_TILES_Y // 2
        startx = focus.x - half_x
        starty = focus.y - half_y
    
    global last_x, last_y
    last_x = startx
    last_y = starty

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
            logging.debug("Drawing %s" % e.name)
            screen.blit(e.get_icon(), ((e.x-startx)*TILE_WIDTH, (e.y-starty)*TILE_HEIGHT))
