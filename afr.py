import random, sys, pygame, os, time, collections, math, logging

import afr.screen
import afr.util
import afr.entity
import afr.entitycomponents
import afr.map

MAP_WIDTH = 30
MAP_HEIGHT = 23

logging.basicConfig(level=logging.DEBUG)

def draw_map(m, screen, startx=0, starty=0, clamp_to_map=True):
    '''Draw the map starting from x,y'''
    screen.fill((0,0,0))

    # Clamp draw rectangle to map border
    if clamp_to_map:
        if startx + afr.screen.CAMERA_TILES_X > m.width:
            startx = m.width - afr.screen.CAMERA_TILES_X
        if starty + afr.screen.CAMERA_TILES_Y > m.height:
            starty = m.height - afr.screen.CAMERA_TILES_Y

        startx = 0 if startx < 0 else startx
        starty = 0 if starty < 0 else starty

    # Don't try to draw tiles beyond the edge of the map
    endx = max([min([startx + afr.screen.CAMERA_TILES_X, m.width]), 0])
    endy = max([min([starty + afr.screen.CAMERA_TILES_Y, m.height]), 0])
    
    logging.debug("Drawing map from %s, %s to %s, %s" % (startx, starty, endx, endy))

    for j in range(starty, endy):
        for i in range(startx, endx):
            #print("%s,%s" % (i,j))
            if i >= 0 and j >= 0:
                screen.blit(m.map[j][i].tile.icon, (afr.screen.TILE_WIDTH*(i-startx), afr.screen.TILE_HEIGHT*(j-starty)))

    for c in afr.entity.entities:
        if startx <= c.maplocation.x <= endx and starty <= c.maplocation.y <= endy:
            screen.blit(c.creature.typedata.icon if c.creature.alive else c.creature.typedata.icondead, ((c.maplocation.x-startx)*afr.screen.TILE_WIDTH, (c.maplocation.y-starty)*afr.screen.TILE_HEIGHT))

def run_creature_brain(c):
    '''Stupid generic creature brain'''
    if not c.creature.alive: return # dont run ai for dead things
    state = c.creature.brainstate
    
    # Find a target
    target = c.creature.find_combat_target()
    if target:
        state['combat_target'] = target

        # Move towards it / attack it
        if MAP.distance_between(c.maplocation.x,c.maplocation.y,target.maplocation.x,target.maplocation.y) <= math.sqrt(2):
            c.creature.attack(target)
        else:
            (dx, dy) = MAP.pathfind_to(c.maplocation.x, c.maplocation.y, state['combat_target'].maplocation.x, state['combat_target'].maplocation.y)
            c.maplocation.x += dx
            c.maplocation.y += dy
    else:
        # No target, wander around
        if random.random() > 0.5:
            (dx, dy) = MAP.pathfind_to(c.maplocation.x, c.maplocation.y, random.randint(0, MAP.width), random.randint(0, MAP.height))
            c.maplocation.x += dx
            c.maplocation.y += dy

def tick():
    for c in afr.entity.entities:
        run_creature_brain(c)

if __name__ == '__main__':
    try:
        # Mapgen
        MAP = afr.map.Map(MAP_WIDTH, MAP_HEIGHT)
        MAP.generate()
        
        # Test creature init
        afr.entity.entities.append( \
            afr.entity.Entity('Urist', MAP, components = [
                afr.entitycomponents.Creature('dwarf', strength=20, hp=40),
                afr.entitycomponents.MapLocation(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1)),
                ]
            )
        )
        afr.entity.entities.append( \
                    afr.entity.Entity('Urist', MAP, components = [
                        afr.entitycomponents.Creature('dwarf', strength=20, hp=40),
                        afr.entitycomponents.MapLocation(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1)),
                        ]
                    )
                )
        afr.entity.entities.append( \
                            afr.entity.Entity('Urist', MAP, components = [
                                afr.entitycomponents.Creature('dwarf', strength=20, hp=40),
                                afr.entitycomponents.MapLocation(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1)),
                                ]
                            )
                        )
        afr.entity.entities.append( \
            afr.entity.Entity('Gobbo', MAP, components = [
                afr.entitycomponents.Creature('goblin', strength=20, hp=40),
                afr.entitycomponents.MapLocation(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1)),
                ]
            )
        )
        afr.entity.entities.append( \
            afr.entity.Entity('Gobbo', MAP, components = [
                afr.entitycomponents.Creature('goblin', strength=20, hp=40),
                afr.entitycomponents.MapLocation(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1)),
                ]
            )
        )
        afr.entity.entities.append( \
            afr.entity.Entity('Gobbo', MAP, components = [
                afr.entitycomponents.Creature('goblin', strength=20, hp=40),
                afr.entitycomponents.MapLocation(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1)),
                ]
            )
        )        
        # PyGame init
        screen = pygame.display.set_mode((afr.screen.RES_X, afr.screen.RES_Y))
        screen.fill((0,0,0))
        pygame.key.set_repeat(400, 50)

        # Event loop
        n_tick = 0
        run = True
        do_tick = False
        update_screen = True
        while run == True:
            if do_tick:
                n_tick += 1
                logging.debug("Tick: %s" % n_tick)
                do_tick = False
                tick()
                print(afr.entity.entities)
                update_screen = True
            if update_screen == True:
                draw_map(MAP, screen, startx=0, starty=0)
                pygame.display.update()
                update_screen = False

            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    do_tick = True
                elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                    run = False
    except:
        raise
    finally:
        pygame.quit()
    sys.exit()
