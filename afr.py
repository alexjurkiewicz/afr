"""AFR main program."""

import logging
import sys

import afr.entity
import afr.entitycomponents
import afr.map
import afr.screen
import afr.util

logging.basicConfig(level=logging.DEBUG,
                    format="%(filename)s (%(funcName)s) %(message)s")

MAP_WIDTH = 40
MAP_HEIGHT = 40

def tick():
    for e in afr.entity.entities:
        if hasattr(e, 'run_ai'):
            logging.debug("Running AI for %s" % e.name)
            e.run_ai()

def main():
    try:
        # Mapgen
        afr.map.CreateMap(width=MAP_WIDTH, height=MAP_HEIGHT)
        afr.map.map.generate_interior(rooms=5)

        # Test creature init
        coords = [afr.map.map.get_empty_coordinates() for i in range(5)]
        afr.entity.entities.append(
            afr.entity.Entity('Urist', components=[
                afr.entitycomponents.Creature(max_hp=100),
                afr.entitycomponents.Fighter(strength=5, team='dwarves'),
                afr.entitycomponents.Corporeal(x=coords[0][0], y=coords[0][1],
                                               icon='@', zorder=1),
                afr.entitycomponents.AI(),
                afr.entitycomponents.Inventory(),
                afr.entitycomponents.Player(),
                ]
            )
        )
        afr.entity.entities.append(
            afr.entity.Entity('Goblin King', components=[
                afr.entitycomponents.Creature(max_hp=40),
                afr.entitycomponents.Fighter(strength=10, team='goblins'),
                afr.entitycomponents.Corporeal(x=coords[1][0], y=coords[1][1]),
                afr.entitycomponents.AI(),
                ]
            )
        )
        afr.entity.entities.append(
            afr.entity.Entity('Sword', components=[
                afr.entitycomponents.Corporeal(x=coords[2][0], y=coords[2][1], icon = '(', blocks_movement = False, zorder = -1),
                afr.entitycomponents.Weapon(strength=10),
                ]
            )
        )
        afr.entity.entities.append(
            afr.entity.Entity('Goblin King', components=[
                afr.entitycomponents.Creature(max_hp=40),
                afr.entitycomponents.Fighter(strength=10, team='goblins'),
                afr.entitycomponents.Corporeal(x=coords[3][0], y=coords[3][1]),
                afr.entitycomponents.AI(),
                ]
            )
        )
        afr.entity.entities.append(
            afr.entity.Entity('Goblin King', components=[
                afr.entitycomponents.Creature(max_hp=40),
                afr.entitycomponents.Fighter(strength=10, team='goblins'),
                afr.entitycomponents.Corporeal(x=coords[4][0], y=coords[4][1]),
                afr.entitycomponents.AI(),
                ]
            )
        )

        # Event loop
        n_tick = 0
        run = True
        while run:
            n_tick += 1
            logging.debug("Tick: %s" % n_tick)
            tick()
            afr.screen.draw_map(afr.map.map, focus=afr.entity.entities[0])

            key = raw_input('_')
            if key == 'q':
                run = False
    except StandardError:
        raise
    sys.exit()

if __name__ == '__main__':
    main()
