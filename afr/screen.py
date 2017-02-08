"""Handles display of the game."""

import logging

import afr.entity
import afr.util

CAMERA_TILES_X = 20
CAMERA_TILES_Y = 20


def draw_map(m, focus=None, clamp_to_map=True):
    """Draw the map."""
    # This is our buffer.
    new_screen = [[' ' for j in range(CAMERA_TILES_Y)]
                  for i in range(CAMERA_TILES_X)]
    # If we have a focus, ensure it's in the midle of the screen
    if focus:
        half_x = CAMERA_TILES_X // 2
        half_y = CAMERA_TILES_Y // 2
        startx = focus.x - half_x
        starty = focus.y - half_y
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

    logging.debug("Drawing map from %s, %s to %s, %s",
                  startx, starty, endx, endy)

    for j in range(starty, endy):
        for i in range(startx, endx):
            if i >= 0 and j >= 0:
                icon = m.getTile(i, j).tile.icon
                x = i - startx
                y = j - starty
                # logging.debug('drawing {icon} at {x},{y}'.format(icon, x, y))
                new_screen[x][y] = icon

    entities_to_draw = {}
    for e in afr.entity.entities:
        if e.has_component('corporeal'):
            if startx <= e.x < endx and starty <= e.y < endy:
                z = e.zorder
                if z in entities_to_draw:
                    entities_to_draw[z].append(e)
                else:
                    entities_to_draw[z] = [e]
    for z in sorted(entities_to_draw.keys()):
        for e in entities_to_draw[z]:
            # logging.debug("Drawing %s" % e.name)
            icon = e.icon
            x = e.x - startx
            y = e.y - starty
            # print 'drawing {icon} at {x},{y}'.format(icon=icon, x=x, y=y)
            new_screen[x][y] = icon

    # Ugly transformation since our buffer is by-column but we print by-row
    for line in range(CAMERA_TILES_Y):
        print(''.join([i[line] for i in new_screen]))
