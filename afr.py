#!/usr/bin/env python

"""AFR main program."""



import logging
import sys

from afr import entity
from afr import entitycomponents
from afr import map as game_map
from afr import player
from afr import screen
from afr import util

logging.basicConfig(level=logging.DEBUG,
                    format="%(filename)s (%(funcName)s) %(message)s")

MAP_WIDTH = 40
MAP_HEIGHT = 40
ALLOWED_KEYS = set('qhjklyubn')


def tick(action):
    """Run game turn. Return success."""
    # XXX: assumes there is only one player entity, but doesn't enforce it
    for e in entity.entities:
        if e.has_component('player'):
            if e.current_hp <= 0:
                logging.info("Game over!")
                sys.exit()
            logging.debug("Handling player action for {}".format(e))
            try:
                player.handle_player_action(action, e)
            except player.ActionError as e:
                logging.info("Couldn't perform action {action} ({reason})"
                             .format(action=action, reason=e))
                return False
    for e in entity.entities:
        if e.has_component('ai') and not e.has_component('player'):
            logging.debug("Running AI for %s" % e.name)
            e.run_ai()
    return True


def main():
    """Main game loop."""
    # Mapgen
    game_map.CreateMap(width=MAP_WIDTH, height=MAP_HEIGHT)
    game_map.map.generate_interior(rooms=5)

    # Test creature init
    coords = [game_map.map.get_empty_coordinates() for i in range(5)]

    p = entity.Entity('Urist', components=[
        entitycomponents.Creature(max_hp=100),
        entitycomponents.Fighter(strength=5, team='dwarves'),
        entitycomponents.Corporeal(x=coords[0][0], y=coords[0][1],
                                       icon='@', zorder=1),
        entitycomponents.AI(),
        entitycomponents.Inventory(),
        entitycomponents.Player(),
    ]
    )
    entity.entities.add(p)

    entity.entities.add(
        entity.Entity('Goblin King', components=[
            entitycomponents.Creature(max_hp=40, size='small'),
            entitycomponents.Fighter(strength=10, team='goblins'),
            entitycomponents.Corporeal(x=coords[1][0], y=coords[1][1]),
            entitycomponents.AI(),
        ]
        )
    )
    entity.entities.add(
        entity.Entity(
            'Sword',
            components=[
                entitycomponents.Corporeal(
                    x=coords[2][0],
                    y=coords[2][1],
                    icon='(',
                    blocks_movement=False,
                    zorder=-1),
                entitycomponents.Equippable(
                    strength=10),
            ]))
    entity.entities.add(
        entity.Entity('Goblin King', components=[
            entitycomponents.Creature(max_hp=40, size='small'),
            entitycomponents.Fighter(strength=10, team='goblins'),
            entitycomponents.Corporeal(x=coords[3][0], y=coords[3][1]),
            entitycomponents.AI(),
        ]
        )
    )
    entity.entities.add(
        entity.Entity('Goblin King', components=[
            entitycomponents.Creature(max_hp=40, size='small'),
            entitycomponents.Fighter(strength=10, team='goblins'),
            entitycomponents.Corporeal(x=coords[4][0], y=coords[4][1]),
            entitycomponents.AI(),
        ]
        )
    )

    # Event loop
    n_tick = 0
    run = True
    while run:
        logging.debug("Tick: %s" % n_tick)
        screen.draw_map(game_map.map, focus=p)
        action = None
        while not action:
            try:
                key = input('>_ ')
            except (EOFError, KeyboardInterrupt):
                print()
                sys.exit(0)
            action = player.key_to_action(key)
            if not action:
                logging.warning("Unknown key '%s'", key)
        did_tick = tick(action=action)
        if did_tick:
            n_tick += 1

    sys.exit()

if __name__ == '__main__':
    main()
