import random, sys, pygame, os, time, collections, math, logging

import afr.screen
import afr.util
import afr.entity
import afr.entitycomponents
import afr.map

MAP_WIDTH = 30
MAP_HEIGHT = 23

logging.basicConfig(level=logging.DEBUG)

def run_creature_brain(c):
    '''Stupid generic creature brain'''
    if not c.fighter.alive: return # dont run ai for dead things
    state = c.fighter.brainstate
    
    # Find a target
    target = c.fighter.find_combat_target()
    if target:
        state['combat_target'] = target

        # Move towards it / attack it
        if MAP.distance_between(c.corporeal.x,c.corporeal.y,target.corporeal.x,target.corporeal.y) <= math.sqrt(2):
            c.fighter.attack(target)
        else:
            (dx, dy) = MAP.pathfind_to(c.corporeal.x, c.corporeal.y, state['combat_target'].corporeal.x, state['combat_target'].corporeal.y)
            c.corporeal.x += dx
            c.corporeal.y += dy
    else:
        # No target, wander around
        if random.random() > 0.5:
            (dx, dy) = MAP.pathfind_to(c.corporeal.x, c.corporeal.y, random.randint(0, MAP.width), random.randint(0, MAP.height))
            c.corporeal.x += dx
            c.corporeal.y += dy

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
                afr.entitycomponents.Fighter('dwarf', strength=20, hp=40, team='dwarves'),
                afr.entitycomponents.Corporeal(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), icon=afr.util.load_icon('horse-head-yellow.png')),
                ]
            )
        )
        afr.entity.entities.append( \
            afr.entity.Entity('Urist', MAP, components = [
                afr.entitycomponents.Fighter('dwarf', strength=20, hp=40, team='dwarves'),
                afr.entitycomponents.Corporeal(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), icon=afr.util.load_icon('horse-head-yellow.png')),
                ]
            )
        )
        afr.entity.entities.append( \
            afr.entity.Entity('Urist', MAP, components = [
                afr.entitycomponents.Fighter('dwarf', strength=20, hp=40, team='dwarves'),
                afr.entitycomponents.Corporeal(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), icon=afr.util.load_icon('horse-head-yellow.png')),
                ]
            )
        )
        afr.entity.entities.append( \
            afr.entity.Entity('Gobbo', MAP, components = [
                afr.entitycomponents.Fighter('goblin', strength=20, hp=40, team='goblins'),
                afr.entitycomponents.Corporeal(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), icon=afr.util.load_icon('imp-laugh-green.png')),
                ]
            )
        )
        afr.entity.entities.append( \
            afr.entity.Entity('Gobbo', MAP, components = [
                afr.entitycomponents.Fighter ('goblin', strength=20, hp=40, team='goblins'),
                afr.entitycomponents.Corporeal(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), icon=afr.util.load_icon('imp-laugh-green.png')),
                ]
            )
        )
        afr.entity.entities.append( \
            afr.entity.Entity('Gobbo', MAP, components = [
                afr.entitycomponents.Fighter('goblin', strength=20, hp=40, team='goblins'),
                afr.entitycomponents.Corporeal(x=random.randint(0, MAP_WIDTH-1), y=random.randint(0, MAP_HEIGHT-1), icon=afr.util.load_icon('imp-laugh-green.png')),
                ]
            )
        )
        # PyGame init
        afr.screen.init_screen()
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
                update_screen = True
            if update_screen == True:
                afr.screen.draw_map(MAP, afr.screen.screen, startx=0, starty=0)
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
