import random, sys, pygame, os, time, collections, math, logging

import afr.screen
import afr.util
import afr.entity
import afr.entitycomponents
import afr.map

MAP_WIDTH = 30
MAP_HEIGHT = 30

logging.basicConfig(level=logging.DEBUG, format="%(filename)s:%(lineno)d (%(funcName)s) %(message)s")

def tick():
    for e in afr.entity.entities:
        if hasattr(e, 'run_ai'):
            logging.debug("Running AI for %s" % e.name)
            e.run_ai()

def main():
    try:
        # Mapgen
        afr.map.CreateMap(width = MAP_WIDTH, height = MAP_HEIGHT)
        afr.map.map.generate()
        
        # Test creature init
        afr.entity.entities.append( \
            afr.entity.Entity('Urist', components = [
                afr.entitycomponents.Creature(max_hp=40),
                afr.entitycomponents.Fighter(strength=5, team='dwarves'),
                afr.entitycomponents.Corporeal(x=1, y=1, icon=afr.util.load_icon('horse-head-yellow.png'), zorder = 1),
                afr.entitycomponents.AI(),
                afr.entitycomponents.Inventory(),
                ]
            )
        )
        afr.entity.entities.append( \
            afr.entity.Entity('Goblin King', components = [
                afr.entitycomponents.Creature(max_hp=40),
                afr.entitycomponents.Fighter(strength=10, team='goblins'),
                afr.entitycomponents.Corporeal(x=15, y=15, icon=afr.util.load_icon('imp-laugh-green.png')),
                afr.entitycomponents.AI(),
                ]
            )
        )
        afr.entity.entities.append( \
            afr.entity.Entity('Sword', components = [
                afr.entitycomponents.Corporeal(x=5, y=5 , icon=afr.util.load_icon('energy-sword.png'), blocks_movement = False, zorder = -1),                
                afr.entitycomponents.Weapon(strength=10),
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
                afr.screen.draw_map(afr.map.map, afr.screen.screen, focus=afr.entity.entities[0])
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

if __name__ == '__main__':
    main()
